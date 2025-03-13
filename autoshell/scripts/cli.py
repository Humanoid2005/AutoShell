from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.prompt import Prompt
from rich.style import Style
from rich.table import Table
from rich import print as rprint
from rich.markdown import Markdown
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.completion import WordCompleter
import inquirer
import subprocess
import os
import time
from typing import List, Optional
import shlex

from autoshell.scripts.db import User,DB
from autoshell.scripts.macros import *
from autoshell.scripts.ai import AI_Models

class AutoshellCLI:
    def __init__(self):
        self.userdata_filename = "users.dat"
        self.user = None
        self.users = []
        self.db = DB()
        self.mode = "manual"
        self.command_history = InMemoryHistory()
        self.commands = ['help', 'clear', 'exit', 'ls', 'cd', 'pwd']
        self.terminal_commands = ['vim', 'neovim', 'nano', 'less', 'more', 'py', 'python', 'python3', 'cmd', 'gdb', 'lldb', 'make', 'cmake', 'svn', 'git', 'ssh', 'telnet']
        self.terminals = ['gnome-terminal', 'xterm', 'konsole', 'bash']
        self.process = None
        self.input = "cd ."
        self.completer = WordCompleter(words=list(self.command_history.get_strings())+self.terminal_commands+self.commands)
        self.console = Console()
        self.ai = AI_Models(self.console)
        #color scheme
        self.ps_blue = "dodger_blue1"
        self.ps_yellow = "bright_yellow"
        self.ps_green = "bright_green"
        self.ps_red = "bright_red"
        self.ps_magenta = "bright_magenta"

    def display_ascii_title(self):
        title_text = """_____         __           _________.__           .__  .__   
  /  _  \\  __ ___/  |_  ____  /   _____/|  |__   ____ |  | |  |  
 /  /_\\  \\|  |  \\   __\\/  _ \\ \\_____  \\ |  |  \\_/ __ \\|  | |  |  
/    |    \\  |  /|  | (  <_> )/        \\|   Y  \\  ___/|  |_|  |__
\\____|__  /____/ |__|  \\____//_______  /|___|  /\\___  >____/____/
        \\/                           \\/      \\/     \\/
        """
        rainbow_colors = ["bright_red", "bright_yellow", "bright_green", "bright_cyan", "bright_blue", "bright_magenta"]
        rainbow_title = Text()
        
        for i, line in enumerate(title_text.splitlines()):
            color = rainbow_colors[i % len(rainbow_colors)]
            rainbow_title.append(line + "\n", style=color)
        
        self.console.print(Panel(rainbow_title, border_style=self.ps_blue))
        self.console.print("The smart devshell with AI superpowers!", style=f"bold {self.ps_yellow}")
        self.console.print("v1.0", style=f"italic {self.ps_blue}")
        self.console.print("")

    def show_loading_spinner(self, message="Loading"):
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task(f"[{self.ps_blue}]{message}...", total=None)
            time.sleep(1)  # Simulate loading time

    def pwd(self) -> str:
        try:
            return os.getcwd()
        except OSError as e:
            return f"Error viewing directory: {e}\n"

    def initialise_user(self,username,password):
        if(self.users==[]):
            users = self.db.read_users()
            for user in users:
                self.users.append(User(user[0],user[1],user[2]))
        
        if(self.user!=None):
            self.user.set_client()
            return SUCCESS
        
        for user in self.users:
            if(user.username==username):
                if(user.password!=password):
                    return INVALID_PASSWORD
                else:
                    self.user = User(user.username,user.password,user.API_KEY)
                    self.user.set_client()
                    return SUCCESS
            
        return USER_NOT_FOUND
    
    def change_api_key(self,API_KEY):
        self.user.API_KEY = API_KEY

        for user in self.users:
            if(user.username==self.user.username and user.password==self.user.password):
                user.API_KEY = API_KEY

        self.db.update_API_KEY(self.user,API_KEY)

    def help(self):
        if(self.user!=None):
            table = Table(show_header=True, header_style=f"bold {self.ps_blue}")
            table.add_column("Command", style="dim")
            table.add_column("Description")
            
            table.add_row("manual <command>", "Manually execute the command")
            table.add_row("ai <prompt>", "Ask AI to find the appropriate command for the input prompt")
            table.add_row("ai-chat <prompt>", "Get guidance to your query on any technical issues")
            table.add_row("change-mode <mode>", "Change shell mode (manual/ai/ai-chat)")
            table.add_row("view-mode", "View the mode of the shell")
            table.add_row("exit", "Exit the shell")
            
            self.console.print(Panel(f"[bold {self.ps_green}]Hello {self.user.username}. Please follow the guide for Autoshell and have fun!"))
            self.console.print(table)
            return SUCCESS
        
        s = "Welcome to Autoshellv1.0\n" + "Let us get started by getting your details\n"
        self.console.print(Panel(s, border_style=self.ps_blue))
        
        username = Prompt.ask("[bold]Enter your username", console=self.console)
        password = Prompt.ask("[bold]Enter your password", console=self.console,password=True)
        
        self.show_loading_spinner("Authenticating")
        is_registered = self.initialise_user(username,password)

        while(is_registered==INVALID_PASSWORD):
            self.console.print("Invalid password", style=f"bold {self.ps_red}")
            username = Prompt.ask("[bold]Enter your username", console=self.console)
            password = Prompt.ask("[bold]Enter your password", console=self.console,password=True)
            self.show_loading_spinner("Authenticating")
            is_registered = self.initialise_user(username,password)

        while(is_registered==USER_NOT_FOUND):
            self.console.print("User not found", style=f"bold {self.ps_yellow}")
            self.console.print("Creating new user account", style=self.ps_blue)
            self.console.print("You can get your Gemini API_KEY at https://aistudio.google.com/app/apikey",style=f"bold {self.ps_green}")
            api_key = Prompt.ask("[bold]Enter your Gemini API_KEY", console=self.console,password=True)
            new_user = User(username,password,api_key)
            self.user = new_user
            self.db.write_user(self.user)
            is_registered = self.initialise_user(username,password)
        
        self.console.print(f"[bold {self.ps_green}]Authentication successful!")

        # User is now registered, show help table
        table = Table(show_header=True, header_style=f"bold {self.ps_blue}")
        table.add_column("Command", style="dim")
        table.add_column("Description")
        
        table.add_row("manual <command>", "Manually execute the command")
        table.add_row("ai <prompt>", "Ask AI to find the appropriate command for the input prompt")
        table.add_row("ai-chat <prompt>", "Get guidance to your query on any technical issues")
        table.add_row("change-mode <mode>", "Change shell mode (manual/ai/ai-chat)")
        table.add_row("view-mode", "View the mode of the shell")
        table.add_row("change-api_key <Gemini API_KEY>","Update your Gemini API key")
        table.add_row("get-cmd-history","Get logs of previously executed shell commands")
        table.add_row("exit", "Exit the shell")
        
        self.console.print(Panel(f"[bold {self.ps_green}]Hello {self.user.username}. Please follow the guide for Autoshell and have fun!"))
        self.console.print(table)

        return SUCCESS

    def start_cli(self):
        self.display_ascii_title()
        self.show_loading_spinner("Initializing AutoShell")
        
        self.console.print("Welcome to AutoShell: [bold blue]The smart devshell![/]", style="bright_white")
        self.console.print("Use this as you would use a regular terminal + your personal AI shell dev", style="dim")
        
        with Progress(
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[bold blue]{task.description} ({task.percentage:.0f}%)"),
        ) as progress:
            task = progress.add_task(f"[{self.ps_blue}]Setting up environment", total=100)
            progress.update(task, advance=50)
            time.sleep(0.5)
            progress.update(task, advance=50)

        self.help()
        return SUCCESS

    def change_mode(self,mode):
        if(mode!="manual" and mode!="ai" and mode !="ai-chat"):
            return INVALID_MODE
        else:
            with Progress(
                SpinnerColumn(),
                BarColumn(),
                TextColumn("[bold blue]{task.description}"),
            ) as progress:
                task = progress.add_task(f"[{self.ps_blue}]Changing mode to {mode}", total=100)
                for i in range(0, 101, 5):
                    time.sleep(0.01)  # Quick animation
                    progress.update(task, completed=i)
            
            self.mode = mode
            self.console.print(f"[bold {self.ps_green}]Mode changed to {mode} successfully!")
    
    def view_mode(self):
        mode_color = {
            "manual": self.ps_blue,
            "ai": self.ps_green,
            "ai-chat": self.ps_magenta
        }.get(self.mode, self.ps_blue)
        
        self.console.print(Panel(
            f"[bold white]{self.user.username}'s shell is in [bold {mode_color}]{self.mode}[/bold {mode_color}] mode",
            border_style=mode_color
        ))

        return SUCCESS
    
    def execute(self,cmd,args):
        try:
            if cmd in self.terminal_commands:
                self.show_loading_spinner(f"Launching {cmd}")
                if os.name == 'nt':  # Windows
                    process = subprocess.Popen(['cmd', '/c', cmd] + args, 
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            text=True,
                                            shell=True)
                    stdout, stderr = process.communicate()
                    if stdout:
                        self.console.print(stdout)
                    if stderr:
                        self.console.print(stderr, style=self.ps_red)
                        return INVALID_COMMAND
                else:  # Linux/Mac
                    for terminal in self.terminals:
                        try:
                            process = subprocess.Popen([terminal, '--', cmd] + args,
                                                        stdout=subprocess.PIPE,
                                                        stderr=subprocess.PIPE,
                                                        text=True)
                            stdout, stderr = process.communicate()
                            if stderr:
                                return INVALID_COMMAND

                        except FileNotFoundError:
                                continue
            elif cmd=="cd":
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[bold blue]{task.description}"),
                    transient=True,
                ) as progress:
                    task = progress.add_task(f"[{self.ps_blue}]Changing directory to {args[0]}...", total=None)
                    os.chdir(args[0])
                    time.sleep(0.1)  # Small delay for animation
                self.console.print(f"Directory changed to [bold]{os.getcwd()}[/bold]", style=self.ps_green)
            elif cmd=="pwd":
                self.console.print(Panel(f"[bold]{os.getcwd()}[/bold]", title="Current Directory", border_style=self.ps_blue))
            elif cmd=="clear":
                subprocess.run("clear")
                self.display_ascii_title()
            if cmd == "doskey" and args and args[0] == "/history":
                # Direct execution for doskey /history
                result = subprocess.run("doskey /history", 
                                    shell=True,
                                    capture_output=True, 
                                    text=True)
                if result.stdout:
                    self.console.print(result.stdout)
                else:
                    self.console.print("No command history available from doskey", style=self.ps_yellow)
                return SUCCESS
            else:
                # For shell features (pipes, &&, redirections), we need to run the full command in a shell
                full_command = cmd
                if args:
                    full_command += ' ' + ' '.join(args)
                    
                if any(char in full_command for char in ['|', '>', '<', '&', ';']):
                    completed_process = subprocess.run(full_command, shell=True)
                else:
                    completed_process = subprocess.run([cmd] + args)
                if completed_process.stdout:
                    self.console.print(completed_process.stdout)
                if completed_process.stderr:
                    self.console.print(completed_process.stderr, style=self.ps_red)
        except Exception as e:
            self.console.print(f'Error: {e}', style=f"bold {self.ps_red}")

    def exit(self):
        # Show exit animation
        with Progress(
            SpinnerColumn(),
            BarColumn(),
            TextColumn("[bold blue]{task.description} ({task.percentage:.0f}%)"),
        ) as progress:
            task = progress.add_task(f"[{self.ps_blue}]Shutting down AutoShell", total=100)
            for i in range(0, 101, 4):
                time.sleep(0.02)
                progress.update(task, completed=i)
        
        self.console.print("[bold green]Goodbye! Have a nice day![/]")
        print()
        exit(0)

    def get_cmd_history(self):
        try:
            # First attempt to save our application's internal command history
            # This should work regardless of platform
            with open("command_logs.txt", "w") as f:
                # Get the commands from our internal history
                history_commands = list(self.command_history.get_strings())
                
                if history_commands:
                    for cmd in history_commands:
                        f.write(f"{cmd}\n")
                    self.console.print(f"Command history saved to command_logs.txt ({len(history_commands)} commands)", style=self.ps_green)
                    return True
                else:
                    # Our internal history is empty, try system history
                    self.console.print("Internal command history is empty, trying system history...", style=self.ps_yellow)
            
            # Try system-specific methods if internal history is empty
            if os.name != 'nt':  # Linux/Mac
                # Create a temporary script to extract history
                with open("get_history.sh", "w") as script:
                    script.write("#!/bin/bash\nhistory > command_logs.txt\n")
                
                # Make it executable
                os.chmod("get_history.sh", 0o755)
                
                # Execute in a new bash session
                subprocess.run(["bash", "-i", "./get_history.sh"])
                
                # Clean up
                os.remove("get_history.sh")
            else:  # Windows
                # For Windows CMD history using doskey
                try:
                    result = subprocess.run(["doskey", "/history"], 
                                        capture_output=True, 
                                        text=True, 
                                        shell=True)
                    with open("command_logs.txt", "w") as f:
                        f.write(result.stdout)
                    # If doskey failed, try PowerShell as fallback
                    if not result.stdout.strip():
                        powershell_cmd = "Get-History | Format-Table -Property CommandLine -HideTableHeaders | Out-File -FilePath command_logs.txt -Encoding utf8"
                        subprocess.run(["powershell", "-Command", powershell_cmd], shell=True)
                except Exception:
                    # Fall back to PowerShell if doskey fails
                    powershell_cmd = "Get-History | Format-Table -Property CommandLine -HideTableHeaders | Out-File -FilePath command_logs.txt -Encoding utf8"
                    subprocess.run(["powershell", "-Command", powershell_cmd], shell=True)
                
        except Exception as e:
            self.console.print(f"Error saving history: {e}", style=self.ps_red)
            return False

    def take_input(self):
        style = Style.from_dict({
            'as': 'bold white',
            'username': 'bold green',
            'cwd': 'bold blue',
        })

        self.input = prompt(
                FormattedText([
                ('class:as', 'AS '),
                ('class:username', f'{self.user.username}-'),
                ('class:cwd', f'{os.getcwd()} $'),
            ]),
            style=style,
            history=self.command_history,
            completer=self.completer
        )
        
        split_input = shlex.split(self.input)
        if not split_input:  # Handle empty input
            return SUCCESS
            
        cmd = split_input[0]
        args = []
        if(len(split_input)>1):
            args = split_input[1:]

        self.console.print("")
        if(cmd=="help"):
            self.help()
        elif(cmd=="exit"):
            self.exit()
        elif(cmd=="change-mode"):
            if not args:
                self.console.print(f"[bold {self.ps_red}]Error: Mode not specified. Usage: change-mode <manual/ai/ai-chat>")
                return INVALID_COMMAND
                
            result = self.change_mode(args[0])
            if(result==INVALID_MODE):
                self.console.print(f"[bold {self.ps_red}]Invalid mode. Valid modes are: manual, ai, ai-chat")
        elif(cmd=="view-mode"):
            self.view_mode()
        elif(cmd=="change-api_key"):
            self.change_api_key(args[0])
        elif(cmd=="get-cmd-history"):
            self.get_cmd_history()
        elif(self.mode=="manual"):
            self.execute(cmd,args)
            self.console.print("") 
        elif(self.mode == "ai"):
            #ai code
            self.console.print("[italic]AI mode is processing your request...[/]", style=self.ps_green)
            with Progress(
                SpinnerColumn(),
                BarColumn(),
                TextColumn("[bold green]{task.description}"),
                transient=True,
            ) as progress:
                task = progress.add_task("[green]Consulting AI...", total=None)
                time.sleep(2)  # Simulate AI processing
            response = self.ai.ai_command_prompting(self.input)
            self.console.print(f"[italic]Command: {response['command']}[/]", style=self.ps_yellow)
            self.console.print(f"[italic]Description: {response['description']}[/]", style=self.ps_magenta)
            command  = response['command'].split()

            questions = [
                inquirer.List('choice',
                            message="Select what you want to do",
                            choices=["Execute Command","Try again","Switch to Manual mode"],
                            ),
            ]
            answers = inquirer.prompt(questions)
            selected_option = answers['choice']
            
            if(selected_option=="Execute Command"):
                if(len(command)>1):
                    self.execute(command[0],command[1:])
                else:
                    self.execute(command[0])
            elif(selected_option=="Try again"):
                return SUCCESS
            elif(selected_option=="Switch to Manual mode"):
                self.mode = "manual"
                return SUCCESS            

        elif(self.mode == "ai-chat"):
            #ai-chat code
            self.console.print("[italic]AI chat mode is processing your request...[/]", style=self.ps_magenta)
            self.ai.cli_technical_chatbot()
            self.change_mode("manual")
        else:
            return INVALID_COMMAND
        
def main():
    try:
        shell = AutoshellCLI()
        shell.start_cli()

        while(True):
            try:
                shell.take_input()
            except KeyboardInterrupt:
                shell.exit()
            except Exception as e:
                continue
    except KeyboardInterrupt:
        shell.exit()
    except Exception as e:
        pass