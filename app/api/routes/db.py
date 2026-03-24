# from fastapi import APIRouter, HTTPException, Query
# from fastapi.responses import FileResponse

# from app.core.paths import ensure_data_dir
# from app.db.connection import connect

# router = APIRouter(prefix='/db', tags=['database'])


# @router.get('/list')
# def list_databases():
#     data_dir = ensure_data_dir()
#     items = []
#     for path in sorted(data_dir.glob('*.duckdb')):
#         items.append({'name': path.name, 'path': str(path), 'size_bytes': path.stat().st_size})
#     return {'databases': items}


# @router.get('/download/{db_name}')
# def download_db(db_name: str):
#     file_path = ensure_data_dir() / db_name
#     if not file_path.exists() or file_path.suffix != '.duckdb':
#         raise HTTPException(status_code=404, detail='База данных не найдена')

#     return FileResponse(
#         path=str(file_path),
#         filename=db_name,
#         media_type='application/octet-stream',
#     )


# @router.get('/summary')
# def db_summary(name: str = Query(..., description='Имя файла базы данных')):
#     db_path = ensure_data_dir() / name
#     if not db_path.exists():
#         raise HTTPException(status_code=404, detail='База данных не найдена')

#     con = connect(db_path, read_only=True)
#     try:
#         counts = con.execute(
#             """
#             SELECT
#                 (SELECT COUNT(*) FROM vk_users),
#                 (SELECT COUNT(*) FROM vk_posts),
#                 (SELECT COUNT(*) FROM vk_comments),
#                 (SELECT COUNT(*) FROM nlp_analysis_posts),
#                 (SELECT COUNT(*) FROM nlp_analysis_comments)
#             """
#         ).fetchone()
#         return {
#             'db_path': str(db_path),
#             'vk_users': counts[0],
#             'vk_posts': counts[1],
#             'vk_comments': counts[2],
#             'nlp_analysis_posts': counts[3],
#             'nlp_analysis_comments': counts[4],
#             'total_records': sum(counts),
#         }
#     finally:
#         con.close()


from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from app.core.paths import ensure_data_dir
import duckdb
import math

router = APIRouter()


def get_db_path(db_name: str):
    data_dir = ensure_data_dir()
    file_path = data_dir / db_name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Database not found")

    return file_path


def quote_ident(name: str) -> str:
    return '"' + str(name).replace('"', '""') + '"'


@router.get("/db/list")
def list_databases():
    data_dir = ensure_data_dir()
    files = [f.name for f in data_dir.glob("*.duckdb")]
    return {"databases": files}


@router.get("/db/download/{db_name}")
def download_db(db_name: str):
    file_path = get_db_path(db_name)
    return FileResponse(
        path=str(file_path),
        filename=db_name,
        media_type="application/octet-stream"
    )


@router.get("/db/tables/{db_name}")
def list_tables(db_name: str):
    file_path = get_db_path(db_name)

    conn = duckdb.connect(str(file_path), read_only=True)
    try:
        tables = conn.execute("SHOW TABLES").fetchall()
        return {"tables": [t[0] for t in tables]}
    finally:
        conn.close()


@router.get("/db/schema/{db_name}/{table_name}")
def get_table_schema(db_name: str, table_name: str):
    file_path = get_db_path(db_name)

    conn = duckdb.connect(str(file_path), read_only=True)
    try:
        rows = conn.execute(f"DESCRIBE {quote_ident(table_name)}").fetchall()
        columns = [{"column_name": row[0], "column_type": row[1]} for row in rows]
        return {"table": table_name, "columns": columns}
    finally:
        conn.close()


@router.get("/db/preview/{db_name}/{table_name}")
def preview_table(
    db_name: str,
    table_name: str,
    limit: int = Query(50, ge=1, le=500)
):
    file_path = get_db_path(db_name)

    conn = duckdb.connect(str(file_path), read_only=True)
    try:
        result = conn.execute(f"SELECT * FROM {quote_ident(table_name)} LIMIT {limit}")
        rows = result.fetchall()
        columns = [desc[0] for desc in result.description]

        clean_rows = []
        for row in rows:
            clean_row = []
            for cell in row:
                if isinstance(cell, float) and (math.isnan(cell) or math.isinf(cell)):
                    clean_row.append(None)
                else:
                    clean_row.append(cell)
            clean_rows.append(clean_row)

        return {
            "table": table_name,
            "columns": columns,
            "rows": clean_rows,
            "limit": limit
        }
    finally:
        conn.close()


@router.get("/db/chart-data/{db_name}/{table_name}")
def chart_data(
    db_name: str,
    table_name: str,
    x_column: str,
    y_column: str | None = None,
    agg: str = Query("count", pattern="^(count|sum|avg|min|max)$"),
    limit: int = Query(20, ge=1, le=200),
    order: str = Query("desc", pattern="^(asc|desc)$")
):
    file_path = get_db_path(db_name)

    q_table = quote_ident(table_name)
    q_x = quote_ident(x_column)
    q_y = quote_ident(y_column) if y_column else None

    if agg == "count":
        metric_sql = "COUNT(*)"
        metric_name = "count"
    else:
        if not y_column:
            raise HTTPException(status_code=400, detail="y_column is required for this aggregation")
        metric_sql = f"{agg.upper()}({q_y})"
        metric_name = f"{agg}_{y_column}"

    sql = f"""
        SELECT {q_x} AS x_value, {metric_sql} AS metric
        FROM {q_table}
        GROUP BY 1
        ORDER BY metric {order.upper()}
        LIMIT {limit}
    """

    conn = duckdb.connect(str(file_path), read_only=True)
    try:
        rows = conn.execute(sql).fetchall()
        labels = [str(r[0]) if r[0] is not None else "NULL" for r in rows]
        values = [float(r[1]) if r[1] is not None else 0 for r in rows]

        return {
            "table": table_name,
            "x_column": x_column,
            "y_column": y_column,
            "aggregation": agg,
            "metric_name": metric_name,
            "labels": labels,
            "values": values
        }
    finally:
        conn.close()

