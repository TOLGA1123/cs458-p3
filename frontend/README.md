# Survey App Frontend

This is the frontend for the Survey App, built with Next.js and TypeScript.

## Prerequisites

- Node.js 18.x or later
- npm or yarn

## Getting Started

1. Install dependencies:
```bash
npm install
# or
yarn install
```

2. Run the development server:
```bash
npm run dev
# or
yarn dev
```

3. Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Project Structure

- `app/` - Contains all the pages and API routes
- `app/api/` - API routes that proxy requests to the Flask backend
- `app/login/` - Login page component
- `public/` - Static assets

## Development

The frontend is built with:
- Next.js 14
- TypeScript
- Tailwind CSS
- React 18

## Backend Integration

The frontend communicates with the Flask backend running on `http://localhost:5000`. Make sure the backend server is running before starting the frontend.

## Building for Production

To build the application for production:

```bash
npm run build
# or
yarn build
```

To start the production server:

```bash
npm run start
# or
yarn start
``` 