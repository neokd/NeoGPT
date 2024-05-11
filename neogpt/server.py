import json
from utils.cprint import cprint


def server(neogpt):
    try:
        import uvicorn
        from fastapi import FastAPI, Request
        from fastapi.responses import StreamingResponse
    except ImportError:
        cprint(
            "Please install FastAPI and Uvicorn to run the server. You can install them using 'pip install fastapi uvicorn'.",
            "red",
        )
        return


    app = FastAPI()

    def send_api_stream(prompt):
        for chunk in neogpt.chat(prompt=prompt["message"], display=False, stream=True):
            yield (
                json.dumps(
                    {
                        "id": chunk.id,
                        "role": "assistant",
                        "type": "message",
                        "content": chunk.choices[0].delta.content,
                    }
                )
                + "\n"
            )

    @app.post("/v1/chat")
    async def chat(request: Request):
        data = await request.json()
        return StreamingResponse(send_api_stream(data), media_type="text/event-stream")

    uvicorn.run(app)
