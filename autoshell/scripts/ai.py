import google.generativeai as genai
import json
from rich import print as rprint
from rich.markdown import Markdown
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.prompt import Prompt
from rich.table import Table
import time
import platform

class AI_Models:
    def __init__(self,console):
        self.console = console

    def ai_command_prompting(self, query):
        context = """ 
            You are a natural language interfaced shell interface which converts the english commands into functional shell commands.
        """
        prompt = f"""
            {context}

            Query: {query}
            
            -Respond taking into consideration that the operating system is {platform.system()}
            -Use pipes (|) and I/O redirection (> , <, >>) to ensure effective commands.
            -When needing to run multiple shell commands in a single line, use pipes (|) to chain commands, unless the commands must be run sequentially regardless of the success of the previous command.
            -Please provide the most optimal and correct shell command corresponding to the english query commands provided by the user.
            -Respond with ONLY a valid JSON object. Do not include any markdown code blocks, text, or other formatting.
            -The JSON object must have keys: "command" and "description".

            Example:
            Query: List all files in the current directory and count the number of lines.
            Response: {{"command": "ls -l | wc -l", "description": "Lists all files and directories in the current directory with detailed information and counts the number of lines."}}
        """

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
        }

        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config,
        )

        response = model.generate_content(prompt)

        try:
            json_data = json.loads(response.text)
            return json_data
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print(f"Response text: {response.text}")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def ai_technical_query(self,query, chat_history):
        """Generates structured responses for technical queries using Gemini."""

        context = """
            You are a highly skilled technical assistant designed to provide clear and accurate answers to complex technical questions.
            Provide detailed explanations, code examples, and relevant links where necessary.
            Maintain a conversational tone but ensure technical accuracy.
            When providing code, make sure to add comments to explain the code.
        """

        prompt = f"""
            {context}

            Chat History:
            {chat_history}

            Query: {query}

            Response:
        """
        model = genai.GenerativeModel('gemini-1.5-pro')

        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error: {e}"

    def cli_technical_chatbot(self):
        """A CLI chatbot for technical queries using Gemini with structured responses."""
        print("Welcome to the Technical CLI Chatbot!")
        chat_history = ""

        style = Style.from_dict({
            'prompt': 'bold blue',
            'response': 'white',
            'error': 'bold red',
        })

        while True:
            try:
                user_input = prompt(HTML('<prompt>You: </prompt>'), style=style)
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("Goodbye!")
                    break
                with Progress(
                    SpinnerColumn(),
                    BarColumn(),
                    TextColumn("[bold magenta]{task.description}"),
                    transient=True,
                ) as progress:
                    task = progress.add_task("[magenta]Consulting AI chat...", total=None)
                    time.sleep(4)
                response = self.ai_technical_query(user_input, chat_history)
                with Progress(
                    SpinnerColumn(),
                    BarColumn(),
                    TextColumn("[bold magenta]{task.description}"),
                    transient=True,
                ) as progress:
                    task = progress.add_task("[magenta]Consulting AI chat...", total=None)
                    time.sleep(2)

                markdown = Markdown(response)
                rprint(f"[bold magenta]Gemini:[/bold magenta]",end=" ") #use rich print.
                self.console.print(markdown)

                # Update chat history (append user input and response)
                chat_history += f"User: {user_input}\nAssistant: {response}\n"

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                rprint(f"[bold red]An error occurred: {e}[/bold red]")