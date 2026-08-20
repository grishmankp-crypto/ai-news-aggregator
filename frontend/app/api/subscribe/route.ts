import { NextResponse } from 'next/server';
import { Pool } from '@neondatabase/serverless';
import crypto from 'crypto';

export async function POST(req: Request) {
  try {
    const { name, email, interests } = await req.json();

    if (!name || !email || !interests || interests.length === 0) {
      return NextResponse.json({ message: 'Missing required fields' }, { status: 400 });
    }

    const pool = new Pool({ connectionString: process.env.DATABASE_URL });

    // Check if user already exists
    const existingUser = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
    if (existingUser.rows.length > 0) {
      // If user exists but is inactive, reactivate them and update interests
      if (!existingUser.rows[0].is_active) {
         await pool.query(
            'UPDATE users SET is_active = true, name = $1, interests = $2 WHERE email = $3',
            [name, JSON.stringify(interests), email]
         );
         return NextResponse.json({ message: 'Account reactivated successfully!' }, { status: 200 });
      }
      return NextResponse.json({ message: 'Email already subscribed' }, { status: 409 });
    }

    const id = crypto.randomUUID();
    const interestsStr = Array.isArray(interests) ? JSON.stringify(interests) : JSON.stringify([interests]);

    // Insert new user
    await pool.query(
      'INSERT INTO users (id, email, name, interests, expertise_level, is_active) VALUES ($1, $2, $3, $4, $5, $6)',
      [id, email, name, interestsStr, 'Intermediate', true]
    );

    return NextResponse.json({ message: 'Successfully subscribed' }, { status: 201 });
  } catch (error) {
    console.error('Subscription error:', error);
    return NextResponse.json({ message: 'Internal server error' }, { status: 500 });
  }
}
