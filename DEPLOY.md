# Deploy SkillBridge

## Render

1. Create a GitHub repository and push this project.
2. In Render, choose **New > Blueprint** and select the repository.
3. Render will use `render.yaml` to install the backend and start FastAPI.
4. Open the deployed URL with `/portal` appended:

```text
https://your-service-name.onrender.com/portal
```

The API documentation is available at `/docs`.

The service must listen on `0.0.0.0` and `$PORT`; both are already configured in `render.yaml`.
