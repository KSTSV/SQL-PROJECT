from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes.collect import router as collect_router
from app.api.routes.db import router as db_router
from app.core.paths import ensure_static_dir

app = FastAPI(
    title='VK SQL Project API',
    version='1.1.0',
    description='API для сбора постов VK по ключевому слову и периоду с сохранением в DuckDB',
)

app.mount('/static', StaticFiles(directory=str(ensure_static_dir())), name='static')

app.include_router(collect_router, prefix='/api')
app.include_router(db_router, prefix='/api')


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return Response(status_code=204)


@app.get('/apple-touch-icon.png', include_in_schema=False)
async def apple_touch_icon():
    return Response(status_code=204)


@app.get('/apple-touch-icon-precomposed.png', include_in_schema=False)
async def apple_touch_icon_precomposed():
    return Response(status_code=204)


# @app.get('/', response_class=HTMLResponse)
# async def root():
#     return """
#     <!DOCTYPE html>
#     <html lang='ru'>
#     <head>
#         <meta charset='UTF-8' />
#         <meta name='viewport' content='width=device-width, initial-scale=1.0' />
#         <title>VK SQL API</title>
#         <style>
#             body {
#                 margin: 0;
#                 min-height: 100vh;
#                 display: flex;
#                 justify-content: center;
#                 align-items: center;
#                 font-family: Arial, sans-serif;
#                 background: linear-gradient(135deg, #0f172a, #1e293b);
#                 color: #e2e8f0;
#             }
#             .card {
#                 width: 460px;
#                 background: rgba(30, 41, 59, 0.96);
#                 border-radius: 18px;
#                 box-shadow: 0 14px 40px rgba(0,0,0,0.35);
#                 padding: 32px;
#             }
#             h1 { margin: 0 0 10px; font-size: 28px; }
#             p { color: #cbd5e1; line-height: 1.5; }
#             .muted { color: #94a3b8; font-size: 14px; }
#             .block { margin-top: 18px; }
#             select, button, input {
#                 width: 100%;
#                 border: none;
#                 border-radius: 10px;
#                 padding: 12px 14px;
#                 box-sizing: border-box;
#                 font-size: 14px;
#             }
#             select, input { background: #f8fafc; color: #0f172a; }
#             button {
#                 background: #3b82f6;
#                 color: white;
#                 cursor: pointer;
#                 margin-top: 10px;
#                 font-weight: 700;
#             }
#             button:hover { background: #2563eb; }
#             button:disabled { background: #475569; cursor: not-allowed; }
#             .secondary {
#                 background: #0f172a;
#                 color: #93c5fd;
#                 border: 1px solid #334155;
#             }
#             .secondary:hover { background: #172554; }
#             .status {
#                 margin-top: 12px;
#                 font-size: 14px;
#                 color: #cbd5e1;
#                 min-height: 20px;
#             }
#             .row { display: grid; gap: 10px; grid-template-columns: 1fr 1fr; }
#             a { color: #93c5fd; text-decoration: none; }
#             code {
#                 display: block;
#                 margin-top: 18px;
#                 background: #020617;
#                 border-radius: 10px;
#                 padding: 12px;
#                 color: #cbd5e1;
#                 font-size: 13px;
#                 white-space: pre-wrap;
#             }
#         </style>
#     </head>
#     <body>
#         <div class='card'>
#             <h1>VK SQL API</h1>
#             <p>Введите keyword и period через Swagger или POST-запрос, после этого база появится в папке <b>data</b> и станет доступна для скачивания.</p>

#             <div class='block'>
#                 <button class='secondary' onclick="window.location.href='/docs'">Открыть Swagger</button>
#             </div>

#             <div class='block'>
#                 <label class='muted' for='dbSelect'>Готовые базы</label>
#                 <select id='dbSelect' style='display:none;'></select>
#                 <button id='downloadBtn' onclick='downloadDB()' disabled>Скачать базу</button>
#                 <div id='status' class='status'>Проверяем наличие баз...</div>
#             </div>

#             <code>POST /api/collect
# GET /api/db/list
# GET /api/db/download/{db_name}
# GET /api/db/summary?name=...</code>
#         </div>

#         <script>
#             async function loadDBs() {
#                 const status = document.getElementById('status');
#                 const select = document.getElementById('dbSelect');
#                 const button = document.getElementById('downloadBtn');

#                 try {
#                     const response = await fetch('/api/db/list');
#                     const data = await response.json();
#                     const databases = data.databases || [];

#                     select.innerHTML = '';

#                     if (databases.length === 0) {
#                         select.style.display = 'none';
#                         button.disabled = true;
#                         status.textContent = 'Базы пока не созданы. Сначала выполните POST /api/collect.';
#                         return;
#                     }

#                     databases.forEach((db) => {
#                         const option = document.createElement('option');
#                         option.value = db.name;
#                         option.textContent = `${db.name} (${db.size_bytes} bytes)`;
#                         select.appendChild(option);
#                     });

#                     select.style.display = 'block';
#                     button.disabled = false;
#                     status.textContent = `Найдено баз: ${databases.length}`;
#                 } catch (error) {
#                     select.style.display = 'none';
#                     button.disabled = true;
#                     status.textContent = 'Не удалось получить список баз.';
#                 }
#             }

#             function downloadDB() {
#                 const select = document.getElementById('dbSelect');
#                 const dbName = select.value;
#                 if (!dbName) {
#                     return;
#                 }
#                 window.location.href = `/api/db/download/${encodeURIComponent(dbName)}`;
#             }

#             loadDBs();
#         </script>
#     </body>
#     </html>
#     """


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8" />
        <title>DuckDB Visual Browser</title>
        <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #0f172a;
                color: #e2e8f0;
                margin: 0;
                padding: 0;
            }
            .wrapper {
                max-width: 1280px;
                margin: 24px auto;
                padding: 16px;
            }
            .card {
                background: #1e293b;
                border-radius: 16px;
                padding: 20px;
                margin-bottom: 18px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.25);
            }
            h1, h2 {
                margin-top: 0;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 14px;
            }
            .grid-4 {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 14px;
            }
            select, button, input {
                width: 100%;
                padding: 10px;
                border-radius: 10px;
                border: none;
                margin-top: 8px;
                margin-bottom: 8px;
                font-size: 14px;
                box-sizing: border-box;
            }
            button {
                background: #3b82f6;
                color: white;
                cursor: pointer;
            }
            button:hover {
                background: #2563eb;
            }
            button:disabled {
                background: #475569;
                cursor: not-allowed;
            }
            .muted {
                color: #94a3b8;
                font-size: 14px;
            }
            #tableWrap {
                overflow-x: auto;
                max-height: 500px;
                overflow-y: auto;
                border-radius: 10px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                background: #0f172a;
            }
            th, td {
                border: 1px solid #334155;
                padding: 8px;
                text-align: left;
                font-size: 13px;
                vertical-align: top;
            }
            th {
                background: #334155;
                position: sticky;
                top: 0;
            }
            a {
                color: #93c5fd;
                text-decoration: none;
            }
            #chart {
                height: 520px;
            }
        </style>
    </head>
    <body>
        <div class="wrapper">
            <div class="card">
                <h1>DuckDB Visual Browser</h1>
                <div class="muted">Интерактивный просмотр и визуализация базы через FastAPI</div>
                <br>
                <a href="/docs">Swagger</a>
            </div>

            <div class="card">
                <h2>1. База и таблица</h2>
                <div class="grid">
                    <div>
                        <label>База</label>
                        <select id="dbSelect"></select>
                    </div>
                    <div>
                        <label>Таблица</label>
                        <select id="tableSelect" disabled></select>
                    </div>
                </div>
                <div class="grid">
                    <button onclick="loadTables()">Загрузить таблицы</button>
                    <button onclick="loadPreview()">Показать данные</button>
                </div>
                <div id="status" class="muted"></div>
            </div>

            <div class="card">
                <h2>2. Настройки графика</h2>
                <div class="grid-4">
                    <div>
                        <label>X колонка</label>
                        <select id="xColumn" disabled></select>
                    </div>
                    <div>
                        <label>Агрегация</label>
                        <select id="aggSelect" disabled>
                            <option value="count">count</option>
                            <option value="sum">sum</option>
                            <option value="avg">avg</option>
                            <option value="min">min</option>
                            <option value="max">max</option>
                        </select>
                    </div>
                    <div>
                        <label>Y колонка</label>
                        <select id="yColumn" disabled></select>
                    </div>
                    <div>
                        <label>Тип графика</label>
                        <select id="chartType">
                            <option value="bar">bar</option>
                            <option value="line">line</option>
                            <option value="pie">pie</option>
                        </select>
                    </div>
                </div>
                <div class="grid">
                    <div>
                        <label>Лимит категорий</label>
                        <input id="limitInput" type="number" value="20" min="1" max="200">
                    </div>
                    <div>
                        <label>Сортировка</label>
                        <select id="orderSelect">
                            <option value="desc">desc</option>
                            <option value="asc">asc</option>
                        </select>
                    </div>
                </div>
                <button id="plotBtn" onclick="buildChart()" disabled>Построить график</button>
            </div>

            <div class="card">
                <h2>3. График</h2>
                <div id="chart"></div>
            </div>

            <div class="card">
                <h2>4. Данные таблицы</h2>
                <div id="tableWrap">
                    <div id="tableResult" class="muted">Пока ничего не загружено</div>
                </div>
            </div>
        </div>

        <script>
            let currentColumns = [];

            async function loadDBs() {
                const res = await fetch('/api/db/list');
                const data = await res.json();

                const dbSelect = document.getElementById('dbSelect');
                dbSelect.innerHTML = '';

                if (!data.databases || data.databases.length === 0) {
                    document.getElementById('status').textContent = 'В папке data нет .duckdb файлов';
                    dbSelect.disabled = true;
                    return;
                }

                data.databases.forEach(db => {
                    const option = document.createElement('option');
                    option.value = db;
                    option.textContent = db;
                    dbSelect.appendChild(option);
                });

                document.getElementById('status').textContent = 'Базы загружены';
            }

            async function loadTables() {
                const db = document.getElementById('dbSelect').value;
                const res = await fetch(`/api/db/tables/${encodeURIComponent(db)}`);
                const data = await res.json();

                const tableSelect = document.getElementById('tableSelect');
                tableSelect.innerHTML = '';

                if (!data.tables || data.tables.length === 0) {
                    tableSelect.disabled = true;
                    document.getElementById('status').textContent = 'В выбранной базе нет таблиц';
                    return;
                }

                data.tables.forEach(table => {
                    const option = document.createElement('option');
                    option.value = table;
                    option.textContent = table;
                    tableSelect.appendChild(option);
                });

                tableSelect.disabled = false;
                document.getElementById('status').textContent = `Таблиц: ${data.tables.length}`;
                await loadSchema();
            }

            async function loadSchema() {
                const db = document.getElementById('dbSelect').value;
                const table = document.getElementById('tableSelect').value;

                const res = await fetch(`/api/db/schema/${encodeURIComponent(db)}/${encodeURIComponent(table)}`);
                const data = await res.json();

                currentColumns = data.columns || [];

                const xColumn = document.getElementById('xColumn');
                const yColumn = document.getElementById('yColumn');
                const aggSelect = document.getElementById('aggSelect');
                const plotBtn = document.getElementById('plotBtn');

                xColumn.innerHTML = '';
                yColumn.innerHTML = '';

                currentColumns.forEach(col => {
                    const opt1 = document.createElement('option');
                    opt1.value = col.column_name;
                    opt1.textContent = `${col.column_name} (${col.column_type})`;
                    xColumn.appendChild(opt1);

                    const opt2 = document.createElement('option');
                    opt2.value = col.column_name;
                    opt2.textContent = `${col.column_name} (${col.column_type})`;
                    yColumn.appendChild(opt2);
                });

                xColumn.disabled = false;
                yColumn.disabled = false;
                aggSelect.disabled = false;
                plotBtn.disabled = false;

                updateYState();
            }

            function updateYState() {
                const agg = document.getElementById('aggSelect').value;
                const yColumn = document.getElementById('yColumn');
                yColumn.disabled = (agg === 'count');
            }

            document.addEventListener('change', function(e) {
                if (e.target && e.target.id === 'aggSelect') {
                    updateYState();
                }
                if (e.target && e.target.id === 'tableSelect') {
                    loadSchema();
                }
            });

            async function loadPreview() {
                const db = document.getElementById('dbSelect').value;
                const table = document.getElementById('tableSelect').value;

                const res = await fetch(`/api/db/preview/${encodeURIComponent(db)}/${encodeURIComponent(table)}?limit=100`);
                const data = await res.json();

                renderTable(data.columns, data.rows);
            }

            async function buildChart() {
                const db = document.getElementById('dbSelect').value;
                const table = document.getElementById('tableSelect').value;
                const x = document.getElementById('xColumn').value;
                const agg = document.getElementById('aggSelect').value;
                const y = document.getElementById('yColumn').value;
                const chartType = document.getElementById('chartType').value;
                const limit = document.getElementById('limitInput').value || 20;
                const order = document.getElementById('orderSelect').value;

                let url = `/api/db/chart-data/${encodeURIComponent(db)}/${encodeURIComponent(table)}?x_column=${encodeURIComponent(x)}&agg=${encodeURIComponent(agg)}&limit=${encodeURIComponent(limit)}&order=${encodeURIComponent(order)}`;

                if (agg !== 'count') {
                    url += `&y_column=${encodeURIComponent(y)}`;
                }

                const res = await fetch(url);
                const data = await res.json();

                if (!data.labels || data.labels.length === 0) {
                    document.getElementById('chart').innerHTML = '<div class="muted">Нет данных для графика</div>';
                    return;
                }

                let trace;
                if (chartType === 'pie') {
                    trace = {
                        labels: data.labels,
                        values: data.values,
                        type: 'pie'
                    };
                } else if (chartType === 'line') {
                    trace = {
                        x: data.labels,
                        y: data.values,
                        type: 'scatter',
                        mode: 'lines+markers'
                    };
                } else {
                    trace = {
                        x: data.labels,
                        y: data.values,
                        type: 'bar'
                    };
                }

                const layout = {
                    title: `${data.aggregation.toUpperCase()} по ${data.x_column}` + (data.y_column ? ` для ${data.y_column}` : ''),
                    paper_bgcolor: '#1e293b',
                    plot_bgcolor: '#1e293b',
                    font: { color: '#e2e8f0' },
                    xaxis: { automargin: true },
                    yaxis: { automargin: true }
                };

                Plotly.newPlot('chart', [trace], layout, {responsive: true});
            }

            function renderTable(columns, rows) {
                const result = document.getElementById('tableResult');

                if (!rows || rows.length === 0) {
                    result.innerHTML = '<div class="muted">Нет данных</div>';
                    return;
                }

                let html = '<table><thead><tr>';
                columns.forEach(col => {
                    html += `<th>${escapeHtml(col)}</th>`;
                });
                html += '</tr></thead><tbody>';

                rows.forEach(row => {
                    html += '<tr>';
                    row.forEach(cell => {
                        html += `<td>${escapeHtml(cell === null ? '' : String(cell))}</td>`;
                    });
                    html += '</tr>';
                });

                html += '</tbody></table>';
                result.innerHTML = html;
            }

            function escapeHtml(value) {
                return value
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/"/g, '&quot;')
                    .replace(/'/g, '&#039;');
            }

            loadDBs();
        </script>
    </body>
    </html>
    """

