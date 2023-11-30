# __Persona & NeoGPT__

## What is Persona?
In the world of artificial intelligence, there's a fascinating quest to make chatbots more interesting and responsive by incorporating personas. NeoGPT takes a creative step in this direction. Think of a persona as a character that NeoGPT takes on to better understand and respond to different situations. It's like giving the model different roles to play, making your interactions more diverse and engaging. NeoGPT supports multiple personas, each with its own role and style, adding a special touch to how it chats with you.

!!! warning "Warning"
    The persona feature is still in beta. We are working on adding more personas and improving the existing ones. Persona's will improve with agents in the future.If you have any suggestions or feedback, please let us know [here](https://github.com/neokd/NeoGPT/issues/new?assignees=&labels=kind-enhancement&projects=&template=enhancement_request.md&title=)


## Available Personas

The following personas are currently available:

- `DEFAULT`: An helpful assistant that will help you with your queries. (default)
- `RECRUITER`: An experienced recruiter who finds the best candidates.
- `ACADEMICIAN`: Engages in in-depth research and presents findings.
- `FRIEND`: Provides comfort and encouragement as a friend.
- `ML_ENGINEER`: Explains complex ML concepts in an easy-to-understand manner.
- `CEO`: Acts as the CEO, making strategic decisions.
- `RESEARCHER`: Analyzes, synthesizes, and provides insights.
- `SHELL`: Executes shell commands.


### Default Persona

Imagine NeoGPT as your ever-reliable assistant. In its default persona, NeoGPT diligently processes the information you provide, responding with thoughtful and step-by-step answers. It doesn't just answer questions; it guides you through the thought process, making your interaction more informative and engaging.

```bash title="Terminal"
python main.py --persona default
```

!!! tip "Tip"
    This is the default persona. You don't need to specify it in the command.


### Recruiter Persona

NeoGPT can also act as a recruiter, helping you find the best candidates for your company. In this persona, NeoGPT asks you a series of questions to understand your requirements and then uses that information to find the best candidates for the job. It is a great way to find the right people for your company and also allowing candidates to showcase their skills.


```bash title="Terminal"
python main.py --persona recruiter
```

### Academician Persona

NeoGPT can also act as an academician, helping you find the best research papers for your research. In this persona, NeoGPT asks you a series of questions to understand your requirements and then uses that information to find the best research papers for your research. It is a great way to find the right research papers for your research and also allowing researchers to showcase their skills.

```bash title="Terminal"
python main.py --persona academician
```

### Friend Persona

NeoGPT's friend persona brings a warm and empathetic touch to your conversations. No need for explanations – this persona is here to offer unwavering support, providing comforting words and positive vibes during life's challenges.

```bash title="Terminal"
python main.py --persona friend
```

### ML Engineer Persona

Tech enthusiasts, rejoice! NeoGPT steps into the shoes of a machine learning engineer, breaking down complex concepts into easy-to-understand terms. Expect step-by-step explanationsand recommendations for further study – a true tech guide..

!!! tip "Tip"
    Perfect for beginners who want to learn more about machine learning. Combine this persona with the test data to get the best results.

```bash title="Terminal"
python main.py --persona ml_engineer
```

### CEO Persona

NeoGPT as a CEO brings strategic thinking to the forefront. Handling challenges, making big decisions, and representing the company – this persona showcases leadership skills, offering insights into the corporate world.

```bash title="Terminal"
python main.py --persona ceo
```

### Researcher Persona

For data exploration and analysis, NeoGPT becomes a researcher. Dive into the world of data with this persona, where NeoGPT sifts through information, analyzes trends and patterns, and presents its findings in a clear and concise manner.

```bash title="Terminal"
python main.py --persona researcher
```

### Shell Persona

NeoGPT's shell persona is a powerful tool for executing shell commands. It can be used to perform a variety of tasks, such as installing software, managing files, and more. However, it is important to note that this persona can be dangerous if used incorrectly. Always review the generated commands before executing them.

```bash title="Terminal"
python main.py --persona shell
```

Refer to the [Executing Shell Commands with NeoGPT 🤖](/NeoGPT/persona/shell) section for more information.


### Conclusion

In essence, NeoGPT's personas transform your chatting experience into a multifaceted journey. Whether you're seeking assistance, strategizing, exploring data, or just having a friendly chat, NeoGPT adapts seamlessly, making it your all-in-one conversational companion.

