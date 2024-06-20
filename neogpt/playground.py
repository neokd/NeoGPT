def playground(neogpt):
    import json

    import uvicorn
    from fastapi import FastAPI, File, Form, Request, UploadFile
    from fastapi.responses import JSONResponse, StreamingResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    from utils.cprint import cprint

    app = FastAPI()
    templates = Jinja2Templates(directory="ui/templates")
    app.mount(
        "/static",
        StaticFiles(directory="./ui/static"),
        name="static",
    )

    @app.get("/chat")
    async def read_root(request: Request):
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
            },
        )

    def send_api_stream(prompt):
        for chunk in neogpt.chat(prompt=prompt["message"], display=False, stream=True):
            yield (
                json.dumps(
                    {
                        "id": chunk.id,
                        "role": "assistant",
                        "type": "message",
                        "content": chunk.choices[0].delta.content,
                        "history": neogpt.messages,
                    }
                )
                + "\n"
            )

    # @app.post("/v1/history")
    # async def history():
    #     return JSONResponse(content={"history": neogpt.messages})

    # @app.post("/v1/update/system-message")
    # async def update_system_message(request: Request):
    #     data = await request.json()
    #     # Get the system message from the neogpt.messages
    #     system_message = next(
    #         (message for message in neogpt.messages if message["role"] == "system"),
    #         None,
    #     )
    #     # Update the system message
    #     if system_message:
    #         system_message["content"] = data["content"]

    #     return JSONResponse(content={"status": "success"})

    # Get last executed terminal output

    @app.post("/v1/chat")
    async def chat(request: Request):
        data = await request.json()
        return StreamingResponse(send_api_stream(data), media_type="text/event-stream")

    cprint("\nServing playground at http://127.0.0.1:8000/chat")
    cprint("Press Ctrl+C to stop the server.")
    uvicorn.run(app, host="127.0.0.1", port=8000)


# Example usage:
# playground(neogpt)
