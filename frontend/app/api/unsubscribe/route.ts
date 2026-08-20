import { NextResponse } from 'next/server';
import { Pool } from '@neondatabase/serverless';

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const email = searchParams.get('email');

  if (!email) {
    return new NextResponse('Missing email parameter', { status: 400 });
  }

  try {
    const pool = new Pool({ connectionString: process.env.DATABASE_URL });
    
    await pool.query('UPDATE users SET is_active = false WHERE email = $1', [email]);

    return new NextResponse(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>Unsubscribed - AI Radar</title>
          <style>
            body { font-family: system-ui, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background-color: #f9fafb; }
            .card { background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; max-width: 400px; }
            h1 { color: #111827; }
            p { color: #4b5563; }
          </style>
        </head>
        <body>
          <div class="card">
            <h1>Successfully Unsubscribed</h1>
            <p>You have been unsubscribed from AI Radar. You will no longer receive daily emails.</p>
          </div>
        </body>
      </html>
    `, {
      headers: { 'Content-Type': 'text/html' },
    });
  } catch (error) {
    console.error('Unsubscribe error:', error);
    return new NextResponse('Internal server error', { status: 500 });
  }
}
