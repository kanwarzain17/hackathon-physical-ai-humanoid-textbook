{
  "version": 2,
  "builds": [
    {
      "src": "backend/api.py",
      "use": "@vercel/python"
    },
    {
      "src": "frontend_book/package.json",
      "use": "@vercel/static-build",
      "config": {
        "buildCommand": "npm run build",
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/api(/.*)?",
      "dest": "backend/api.py"
    },
    {
      "handle": "filesystem"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend_book/build/index.html"
    }
  ]
}
