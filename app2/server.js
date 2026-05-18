const express = require('express');
const { Pool } = require('pg');

const app = express();
const PORT = 3000;

const pool = new Pool({
  host: '127.0.0.1',
  port: 5432,
  database: 'appdb',
  user: process.env.USER || 'runner',
});

const HTML = (title, body) => `<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title}</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; min-height: 100vh; }
    nav {
      background: #1e293b; padding: 0 2rem;
      display: flex; align-items: center; gap: 1rem;
      border-bottom: 1px solid #334155; height: 56px;
    }
    nav .logo { font-size: 1.1rem; font-weight: 700; color: #38bdf8; margin-right: auto; }
    nav a {
      color: #94a3b8; text-decoration: none; padding: 0.4rem 0.9rem;
      border-radius: 6px; font-size: 0.9rem; transition: all .15s;
    }
    nav a:hover, nav a.active { background: #334155; color: #e2e8f0; }
    nav .badge {
      background: #f59e0b; color: #000; font-size: 0.75rem; font-weight: 700;
      padding: 0.25rem 0.6rem; border-radius: 999px;
    }
    .container { max-width: 960px; margin: 2rem auto; padding: 0 1rem; }
    h1 { font-size: 1.6rem; font-weight: 700; margin-bottom: 1.5rem; color: #f1f5f9; }
    h2 { font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; color: #cbd5e1; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
    .card {
      background: #1e293b; border: 1px solid #334155; border-radius: 12px;
      padding: 1.25rem; transition: border-color .2s;
    }
    .card:hover { border-color: #38bdf8; }
    .card .label { font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: .05em; margin-bottom: .4rem; }
    .card .value { font-size: 2rem; font-weight: 700; color: #38bdf8; }
    .card .sub { font-size: 0.8rem; color: #64748b; margin-top: .25rem; }
    table { width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 10px; overflow: hidden; }
    thead { background: #0f172a; }
    th { padding: .75rem 1rem; text-align: left; font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: .05em; }
    td { padding: .75rem 1rem; border-top: 1px solid #334155; font-size: 0.9rem; }
    tr:hover td { background: #263146; }
    .pill {
      display: inline-block; padding: .2rem .65rem; border-radius: 999px;
      font-size: 0.75rem; font-weight: 600;
    }
    .pill-blue { background: #1e3a5f; color: #38bdf8; }
    .pill-green { background: #14532d; color: #4ade80; }
    .pill-purple { background: #3b0764; color: #c084fc; }
    .section { margin-bottom: 2.5rem; }
    .empty { color: #64748b; font-style: italic; padding: 1.5rem; text-align: center; }
    .error { background: #450a0a; border: 1px solid #7f1d1d; border-radius: 10px; padding: 1rem; color: #fca5a5; }
    pre { background: #0f172a; padding: 1rem; border-radius: 8px; overflow-x: auto; font-size: 0.8rem; color: #a3e635; line-height: 1.6; }
    .back { display:inline-block; margin-bottom:1rem; color:#38bdf8; text-decoration:none; font-size:.9rem; }
    .back:hover { text-decoration: underline; }
    form { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem; }
    label { display:block; font-size:.85rem; color:#94a3b8; margin-bottom:.3rem; }
    input, select {
      width:100%; background:#0f172a; border:1px solid #334155; border-radius:6px;
      padding:.5rem .75rem; color:#e2e8f0; font-size:.9rem; margin-bottom:1rem;
    }
    button { background:#38bdf8; color:#0f172a; font-weight:700; padding:.5rem 1.2rem; border:none; border-radius:6px; cursor:pointer; font-size:.9rem; }
    button:hover { background:#7dd3fc; }
  </style>
</head>
<body>
  <nav>
    <span class="logo">&#9670; Node Admin</span>
    <a href="/" ${title==='Dashboard' ? 'class="active"' : ''}>Dashboard</a>
    <a href="/students" ${title.includes('Student') ? 'class="active"' : ''}>Students</a>
    <a href="/courses" ${title.includes('Course') ? 'class="active"' : ''}>Courses</a>
    <a href="/grades" ${title.includes('Grade') ? 'class="active"' : ''}>Grades</a>
    <a href="/sql" ${title==='SQL Console' ? 'class="active"' : ''}>SQL Console</a>
    <span class="badge">Node.js</span>
  </nav>
  <div class="container">${body}</div>
</body>
</html>`;

// ── Dashboard ─────────────────────────────────────────────
app.get('/', async (req, res) => {
  try {
    const [s, c, g, v] = await Promise.all([
      pool.query('SELECT COUNT(*) FROM students'),
      pool.query('SELECT COUNT(*) FROM courses'),
      pool.query('SELECT COUNT(*) FROM grades'),
      pool.query('SELECT version()'),
    ]);
    const pgVer = v.rows[0].version.split(' ').slice(0,2).join(' ');
    const body = `
      <h1>Dashboard</h1>
      <div class="grid">
        <div class="card"><div class="label">Students</div><div class="value">${s.rows[0].count}</div><div class="sub">in appdb</div></div>
        <div class="card"><div class="label">Courses</div><div class="value">${c.rows[0].count}</div><div class="sub">in appdb</div></div>
        <div class="card"><div class="label">Grades</div><div class="value">${g.rows[0].count}</div><div class="sub">records</div></div>
        <div class="card"><div class="label">Database</div><div class="value" style="font-size:1.1rem;line-height:1.4">${pgVer}</div><div class="sub">PostgreSQL</div></div>
      </div>
      <div class="section">
        <h2>Recent Grades</h2>
        ${await recentGradesTable()}
      </div>`;
    res.send(HTML('Dashboard', body));
  } catch (e) {
    res.send(HTML('Dashboard', `<div class="error">DB error: ${e.message}</div>`));
  }
});

async function recentGradesTable() {
  const r = await pool.query(`
    SELECT s.name AS student, c.title AS course, g.grade
    FROM grades g
    JOIN students s ON s.id = g.student_id
    JOIN courses  c ON c.id = g.course_id
    ORDER BY g.id DESC LIMIT 5`);
  if (!r.rows.length) return '<p class="empty">No grades yet.</p>';
  return `<table><thead><tr><th>Student</th><th>Course</th><th>Grade</th></tr></thead><tbody>
    ${r.rows.map(r => `<tr><td>${r.student}</td><td>${r.course}</td><td><span class="pill pill-green">${r.grade}</span></td></tr>`).join('')}
  </tbody></table>`;
}

// ── Students ─────────────────────────────────────────────
app.get('/students', async (req, res) => {
  try {
    const r = await pool.query('SELECT * FROM students ORDER BY id');
    const rows = r.rows.map(s => `<tr><td>${s.id}</td><td>${s.name}</td><td>${s.email}</td></tr>`).join('');
    const body = `
      <h1>Students</h1>
      <div class="section">
        <table><thead><tr><th>ID</th><th>Name</th><th>Email</th></tr></thead>
        <tbody>${rows || '<tr><td colspan="3" class="empty">No students</td></tr>'}</tbody></table>
      </div>`;
    res.send(HTML('Students', body));
  } catch (e) {
    res.send(HTML('Students', `<div class="error">${e.message}</div>`));
  }
});

// ── Courses ──────────────────────────────────────────────
app.get('/courses', async (req, res) => {
  try {
    const r = await pool.query('SELECT * FROM courses ORDER BY id');
    const rows = r.rows.map(c => `<tr><td>${c.id}</td><td>${c.title}</td><td><span class="pill pill-purple">${c.credits}</span></td></tr>`).join('');
    const body = `
      <h1>Courses</h1>
      <div class="section">
        <table><thead><tr><th>ID</th><th>Title</th><th>Credits</th></tr></thead>
        <tbody>${rows || '<tr><td colspan="3" class="empty">No courses</td></tr>'}</tbody></table>
      </div>`;
    res.send(HTML('Courses', body));
  } catch (e) {
    res.send(HTML('Courses', `<div class="error">${e.message}</div>`));
  }
});

// ── Grades ───────────────────────────────────────────────
app.get('/grades', async (req, res) => {
  try {
    const r = await pool.query(`
      SELECT g.id, s.name AS student, c.title AS course, g.grade
      FROM grades g
      JOIN students s ON s.id = g.student_id
      JOIN courses  c ON c.id = g.course_id
      ORDER BY g.id`);
    const rows = r.rows.map(g =>
      `<tr><td>${g.id}</td><td>${g.student}</td><td>${g.course}</td><td><span class="pill pill-green">${g.grade}</span></td></tr>`
    ).join('');
    const body = `
      <h1>Grades</h1>
      <div class="section">
        <table><thead><tr><th>ID</th><th>Student</th><th>Course</th><th>Grade</th></tr></thead>
        <tbody>${rows || '<tr><td colspan="4" class="empty">No grades</td></tr>'}</tbody></table>
      </div>`;
    res.send(HTML('Grades', body));
  } catch (e) {
    res.send(HTML('Grades', `<div class="error">${e.message}</div>`));
  }
});

// ── SQL Console ──────────────────────────────────────────
app.get('/sql', (req, res) => {
  res.send(HTML('SQL Console', `
    <h1>SQL Console</h1>
    <form method="POST" action="/sql">
      <label>SQL Query</label>
      <textarea name="query" rows="4" style="width:100%;background:#0f172a;border:1px solid #334155;border-radius:6px;padding:.5rem .75rem;color:#e2e8f0;font-size:.9rem;font-family:monospace;margin-bottom:1rem;" placeholder="SELECT * FROM students LIMIT 10;"></textarea>
      <button type="submit">Run Query</button>
    </form>`));
});

app.use(express.urlencoded({ extended: true }));

app.post('/sql', async (req, res) => {
  const query = (req.body.query || '').trim();
  let resultHtml = '';
  if (query) {
    try {
      const r = await pool.query(query);
      if (r.rows && r.rows.length) {
        const cols = Object.keys(r.rows[0]);
        resultHtml = `<h2>Result — ${r.rows.length} row(s)</h2>
          <table><thead><tr>${cols.map(c => `<th>${c}</th>`).join('')}</tr></thead>
          <tbody>${r.rows.map(row =>
            `<tr>${cols.map(c => `<td>${row[c] ?? '<span style="color:#64748b">NULL</span>'}</td>`).join('')}</tr>`
          ).join('')}</tbody></table>`;
      } else {
        resultHtml = `<p style="color:#4ade80;margin-top:1rem">✓ OK — ${r.rowCount} row(s) affected.</p>`;
      }
    } catch (e) {
      resultHtml = `<div class="error" style="margin-top:1rem">${e.message}</div>`;
    }
  }
  res.send(HTML('SQL Console', `
    <h1>SQL Console</h1>
    <form method="POST" action="/sql">
      <label>SQL Query</label>
      <textarea name="query" rows="4" style="width:100%;background:#0f172a;border:1px solid #334155;border-radius:6px;padding:.5rem .75rem;color:#e2e8f0;font-size:.9rem;font-family:monospace;margin-bottom:1rem;">${query}</textarea>
      <button type="submit">Run Query</button>
    </form>${resultHtml}`));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Node Admin running on port ${PORT}`);
});
