# import os
# from datetime import datetime

# from langchain.schema import AIMessage, HumanMessage
# from rich.console import Console
# from rich.prompt import Prompt
# from rich.rule import Rule
# from rich.table import Table


def conversation_navigator():
    pass


# from settings import Settings

# console = Console()


# def cprint(*args, **kwargs):
#     return console.print(*args, **kwargs)


# def get_file_date_time(file_name):
#     try:
#         # Extract date and time from the file name
#         date_str = file_name.split("_")[2].replace(".txt", "")
#         time_str = file_name.split("_")[3].replace(".txt", "")
#         date_time_str = date_str + "_" + time_str

#         date_time = datetime.strptime(date_time_str, "%Y%m%d_%H%M%S")
#         return date_time.strftime("%Y-%m-%d %H:%M:%S")
#     except (IndexError, ValueError):
#         return "Invalid Date and Time"


# def conversation_navigator(chain):
#     console.clear()
#     # List all files in the conversation memory directory

#     table = Table(
#         title="Chat History: 📖",
#         show_header=True,
#         header_style="bold magenta",
#         title_justify="center",
#         width=console.width,
#     )
#     table.add_column("S.No.", justify="center")
#     table.add_column("File Name", justify="center")
#     table.add_column("File Content", justify="center")
#     table.add_column("Date & Time", justify="center")

#     # Show number with file name, date, and time
#     files = os.listdir(CONVERSTAION_MEMORY_DIRECTORY)
#     if len(files) == 0:
#         cprint(
#             "\nNo chat history available. Save the chat history using [bold cyan]/save[/bold cyan] command. Start chatting with NeoGPT to see the history."
#         )
#         return
#     for i, file in enumerate(files, start=1):
#         date_time = get_file_date_time(file)
#         # cprint(
#         #     f"[bold blue]{i}. {file}[/bold blue] \t\t\t\t\t [blue dim]{date_time}[/blue dim]"
#         # )
#         with open(os.path.join(Settings.CONVERSATION_DIR, file)) as f:
#             content = f.read()
#             if len(content) > 100:
#                 content = content[:20] + "..."
#             table.add_row(str(i), file, content, date_time)
#         # table.add_row(str(i), file, date_time)
#     cprint(table)
#     cprint("\n")
#     # Prompt the user to select a file
#     cprint("[dim]Enter 'q' to go back to [/dim]")
#     file_number = Prompt.ask("Enter the file number to load the conversation")

#     if file_number == "q":
#         console.clear()
#         return
#     file_number = int(file_number)
#     # Validate the input
#     if 1 <= file_number <= len(files):
#         selected_file = files[file_number - 1]
#         cprint(f"\nLoading conversation from [bold cyan]{selected_file}[/bold cyan]...")
#         with open(os.path.join(CONVERSTAION_MEMORY_DIRECTORY, selected_file)) as f:
#             content = f.read()
#             if isinstance(content, str):
#                 content = content.split("\n")
#                 for line in content:
#                     if line.startswith("NeoGPT: "):
#                         chain.combine_documents_chain.memory.chat_memory.messages.append(
#                             AIMessage(content=line.replace("NeoGPT: ", "").strip())
#                         )
#                     else:
#                         chain.combine_documents_chain.memory.chat_memory.messages.append(
#                             HumanMessage(content=line)
#                         )
#             else:
#                 cprint("invalid file")
#         return
#     else:
#         cprint(
#             "[bold red]Invalid file number. Please enter a valid file number.[/bold red]"
#         )
#         console.clear()
#         return
