# =============================================================================
# app.py — Dashboard Frontend del Sistema de Inventario de Equipos TI
# Streamlit + Plotly | Proyecto Final SO2 — Antonio Samayoa
# =============================================================================

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Inventario TI",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #0f3460 0%, #16213e 50%, #0f3460 100%);
        padding: 20px 30px; border-radius: 12px;
        border-left: 5px solid #00d4ff; margin-bottom: 24px;
    }
    .main-header h1 { color: #00d4ff; margin: 0; font-size: 2rem; }
    .main-header p  { color: #94a3b8; margin: 4px 0 0 0; }
    .kpi-card { background: #1e293b; border-radius: 12px; padding: 20px;
                text-align: center; border-top: 4px solid; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
    .kpi-number { font-size: 2.8rem; font-weight: 800; margin: 8px 0; }
    .kpi-label  { font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }
    .section-title { color: #00d4ff; font-size: 1.1rem; font-weight: 700;
                     border-bottom: 2px solid #1e293b; padding-bottom: 8px; margin: 16px 0; }
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Helpers API ────────────────────────────────────────────────────────────────
def api_get(path):
    try:
        r = requests.get(f"{API_URL}{path}", timeout=5)
        return r.json() if r.status_code == 200 else []
    except: return []

def api_post(path, data):
    try: return requests.post(f"{API_URL}{path}", json=data, timeout=5)
    except Exception as e: return type("R", (), {"status_code": 500, "text": str(e)})()

def api_put(path, data):
    try: return requests.put(f"{API_URL}{path}", json=data, timeout=5)
    except Exception as e: return type("R", (), {"status_code": 500, "text": str(e)})()

def api_delete(path):
    try: return requests.delete(f"{API_URL}{path}", timeout=5)
    except Exception as e: return type("R", (), {"status_code": 500, "text": str(e)})()

def check_api():
    try: return requests.get(f"{API_URL}/health", timeout=3).status_code == 200
    except: return False

@st.cache_data(ttl=8)
def load_equipos():      return api_get("/equipos/?limit=200")
@st.cache_data(ttl=8)
def load_departamentos(): return api_get("/departamentos/?limit=200")
@st.cache_data(ttl=8)
def load_asignaciones():  return api_get("/asignaciones/?limit=200")

def reload():
    st.cache_data.clear()
    st.rerun()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🖥️ Inventario TI")
    st.markdown("---")
    st.success("🟢 API Conectada") if check_api() else st.error("🔴 API Desconectada")
    st.markdown("---")
    pagina = st.radio("", [
        "📊 Dashboard",
        "🖥️ Equipos",
        "🏢 Departamentos",
        "👤 Asignaciones",
        "📋 Historial Auditoría",
    ], label_visibility="collapsed")
    st.markdown("---")
    if st.button("🔄 Refrescar", use_container_width=True):
        reload()
    st.markdown("""
    <div style='font-size:0.75rem;color:#64748b;text-align:center;margin-top:12px'>
        Proyecto Final SO2<br>
        <b style='color:#00d4ff'>Antonio Samayoa</b><br>
        FastAPI · PostgreSQL · Docker Swarm · AWS
    </div>""", unsafe_allow_html=True)

# ── Datos globales ─────────────────────────────────────────────────────────────
equipos       = load_equipos()
departamentos = load_departamentos()
asignaciones  = load_asignaciones()
dep_map  = {d["id"]: d["nombre"] for d in departamentos}
eq_map   = {e["id"]: e["nombre"] for e in equipos}

# ==============================================================================
# PÁGINA: DASHBOARD
# ==============================================================================
if pagina == "📊 Dashboard":
    st.markdown("""<div class="main-header">
        <h1>🖥️ Sistema de Inventario de Equipos TI</h1>
        <p>Dashboard de monitoreo · Proyecto Final Sistemas Operativos II</p>
    </div>""", unsafe_allow_html=True)

    if not equipos:
        st.warning("⚠️ Sin datos. Verifica que la API esté corriendo.")
        st.stop()

    df = pd.DataFrame(equipos)
    df["departamento"] = df["departamento_id"].map(dep_map).fillna("Sin departamento")

    total     = len(df)
    asignados = len(df[df["estado"] == "asignado"])
    bodega    = len(df[df["estado"] == "bodega"])
    mant      = len(df[df["estado"] == "mantenimiento"])

    k1, k2, k3, k4 = st.columns(4)
    for col, label, val, color in [
        (k1, "TOTAL EQUIPOS",  total,     "#00d4ff"),
        (k2, "ASIGNADOS",      asignados, "#22c55e"),
        (k3, "EN BODEGA",      bodega,    "#3b82f6"),
        (k4, "MANTENIMIENTO",  mant,      "#f59e0b"),
    ]:
        with col:
            st.markdown(f"""<div class="kpi-card" style="border-color:{color}">
                <div class="kpi-label">{label}</div>
                <div class="kpi-number" style="color:{color}">{val}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="section-title">📊 Equipos por Estado</div>', unsafe_allow_html=True)
        fig = px.pie(df["estado"].value_counts().reset_index().rename(columns={"estado":"Estado","count":"N"}),
                     values="N", names="Estado", hole=0.45,
                     color="Estado", color_discrete_map={"asignado":"#22c55e","bodega":"#3b82f6","mantenimiento":"#f59e0b"})
        fig.update_layout(paper_bgcolor="#1e293b", plot_bgcolor="#1e293b", font_color="#e2e8f0",
                          margin=dict(t=20,b=20), legend=dict(bgcolor="#1e293b"))
        fig.update_traces(textfont_color="#e2e8f0", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<div class="section-title">🏢 Equipos por Departamento</div>', unsafe_allow_html=True)
        dc = df["departamento"].value_counts().reset_index().rename(columns={"departamento":"Departamento","count":"N"})
        fig2 = px.bar(dc, x="N", y="Departamento", orientation="h",
                      color="N", color_continuous_scale=["#1e40af","#00d4ff"])
        fig2.update_layout(paper_bgcolor="#1e293b", plot_bgcolor="#1e293b", font_color="#e2e8f0",
                           margin=dict(t=20,b=20), coloraxis_showscale=False,
                           xaxis=dict(gridcolor="#334155"), yaxis=dict(gridcolor="#334155"))
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="section-title">💻 Equipos por Tipo</div>', unsafe_allow_html=True)
        tc = df["tipo"].value_counts().reset_index().rename(columns={"tipo":"Tipo","count":"N"})
        tc["Tipo"] = tc["Tipo"].map({"laptop":"💻 Laptop","switch_poe":"🔌 Switch POE","servidor":"🖧 Servidor"}).fillna(tc["Tipo"])
        fig3 = px.bar(tc, x="Tipo", y="N", color="Tipo",
                      color_discrete_sequence=["#00d4ff","#7c3aed","#059669"])
        fig3.update_layout(paper_bgcolor="#1e293b", plot_bgcolor="#1e293b", font_color="#e2e8f0",
                           showlegend=False, margin=dict(t=20,b=20),
                           xaxis=dict(gridcolor="#334155"), yaxis=dict(gridcolor="#334155"))
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        st.markdown('<div class="section-title">📋 Últimas Asignaciones</div>', unsafe_allow_html=True)
        if asignaciones:
            df_a = pd.DataFrame(asignaciones[:6])
            df_a["equipo"] = df_a["equipo_id"].map(eq_map).fillna("—")
            st.dataframe(df_a[["equipo","responsable","fecha_asignacion"]].rename(columns={
                "equipo":"Equipo","responsable":"Responsable","fecha_asignacion":"Fecha"}),
                use_container_width=True, hide_index=True)
        else:
            st.info("No hay asignaciones.")

# ==============================================================================
# PÁGINA: EQUIPOS
# ==============================================================================
elif pagina == "🖥️ Equipos":
    st.markdown("## 🖥️ Equipos")
    tab_ver, tab_nuevo, tab_editar, tab_eliminar = st.tabs(
        ["📋 Ver todos", "➕ Registrar", "✏️ Editar", "🗑️ Eliminar"])

    # ── Ver ──
    with tab_ver:
        if not equipos:
            st.warning("Sin equipos."); st.stop()
        df = pd.DataFrame(equipos)
        df["departamento"] = df["departamento_id"].map(dep_map).fillna("Sin departamento")

        c1, c2, c3 = st.columns(3)
        f_tipo   = c1.selectbox("Tipo",   ["Todos","laptop","switch_poe","servidor"])
        f_estado = c2.selectbox("Estado", ["Todos","asignado","bodega","mantenimiento"])
        f_dep    = c3.selectbox("Departamento", ["Todos"]+list(dep_map.values()))

        dff = df.copy()
        if f_tipo   != "Todos": dff = dff[dff["tipo"]        == f_tipo]
        if f_estado != "Todos": dff = dff[dff["estado"]      == f_estado]
        if f_dep    != "Todos": dff = dff[dff["departamento"] == f_dep]

        st.caption(f"{len(dff)} equipo(s) encontrado(s)")

        def color_estado(val):
            return {"asignado":"background-color:#166534;color:#86efac",
                    "bodega":"background-color:#1e3a5f;color:#93c5fd",
                    "mantenimiento":"background-color:#7c2d12;color:#fdba74"}.get(val,"")

        disp = dff[["id","nombre","tipo","estado","numero_serie","departamento"]].rename(columns={
            "id":"ID","nombre":"Nombre","tipo":"Tipo","estado":"Estado",
            "numero_serie":"N° Serie","departamento":"Departamento"})
        st.dataframe(disp.style.map(color_estado, subset=["Estado"]),
                     use_container_width=True, hide_index=True, height=420)

    # ── Nuevo ──
    with tab_nuevo:
        st.markdown("### Registrar nuevo equipo")
        with st.form("f_eq_nuevo", clear_on_submit=True):
            c1, c2 = st.columns(2)
            nombre  = c1.text_input("Nombre *", placeholder="Dell Latitude 5560")
            serie   = c1.text_input("N° Serie *", placeholder="DL5560-011-GT")
            tipo    = c2.selectbox("Tipo *", ["laptop","switch_poe","servidor"])
            estado  = c2.selectbox("Estado inicial", ["bodega","asignado","mantenimiento"])
            dep_sel = st.selectbox("Departamento", ["Sin departamento"]+list(dep_map.values()))
            dep_id  = {v:k for k,v in dep_map.items()}.get(dep_sel)
            if st.form_submit_button("💾 Registrar", use_container_width=True):
                if not nombre or not serie:
                    st.error("❌ Nombre y N° Serie son obligatorios.")
                else:
                    r = api_post("/equipos/", {"nombre":nombre,"tipo":tipo,"estado":estado,
                                               "numero_serie":serie,"departamento_id":dep_id})
                    if r.status_code == 201:
                        st.success(f"✅ **{nombre}** registrado."); reload()
                    elif r.status_code == 409:
                        st.error(f"❌ Serie **{serie}** ya existe.")
                    else:
                        st.error(f"❌ Error {r.status_code}: {r.text}")

    # ── Editar ──
    with tab_editar:
        st.markdown("### Editar equipo existente")
        if not equipos:
            st.info("Sin equipos."); st.stop()
        opts = {f"{e['id']} — {e['nombre']} ({e['estado']})": e for e in equipos}
        sel  = st.selectbox("Selecciona equipo", list(opts.keys()), key="sel_edit_eq")
        eq   = opts[sel]
        with st.form("f_eq_edit"):
            c1, c2 = st.columns(2)
            new_nombre = c1.text_input("Nombre", value=eq["nombre"])
            new_serie  = c1.text_input("N° Serie", value=eq["numero_serie"])
            new_tipo   = c2.selectbox("Tipo", ["laptop","switch_poe","servidor"],
                         index=["laptop","switch_poe","servidor"].index(eq["tipo"]))
            new_estado = c2.selectbox("Estado", ["bodega","asignado","mantenimiento"],
                         index=["bodega","asignado","mantenimiento"].index(eq["estado"]))
            dep_nombres = ["Sin departamento"]+list(dep_map.values())
            dep_actual  = dep_map.get(eq.get("departamento_id"), "Sin departamento")
            dep_sel  = st.selectbox("Departamento", dep_nombres,
                       index=dep_nombres.index(dep_actual) if dep_actual in dep_nombres else 0)
            new_dep_id = {v:k for k,v in dep_map.items()}.get(dep_sel)

            if eq["estado"] != new_estado:
                st.info(f"⚡ El trigger SQL registrará: **{eq['estado']}** → **{new_estado}**")

            if st.form_submit_button("💾 Guardar cambios", use_container_width=True):
                r = api_put(f"/equipos/{eq['id']}", {"nombre":new_nombre,"tipo":new_tipo,
                            "estado":new_estado,"numero_serie":new_serie,"departamento_id":new_dep_id})
                if r.status_code == 200:
                    st.success("✅ Equipo actualizado."); reload()
                else:
                    st.error(f"❌ Error {r.status_code}: {r.text}")

    # ── Eliminar ──
    with tab_eliminar:
        st.markdown("### Eliminar equipo")
        st.warning("⚠️ Esta acción es irreversible.")
        opts = {f"{e['id']} — {e['nombre']} | {e['estado']}": e for e in equipos}
        sel  = st.selectbox("Selecciona equipo", list(opts.keys()), key="sel_del_eq")
        eq   = opts[sel]
        st.markdown(f"""<div style="background:#2b0d0d;border-radius:10px;padding:14px;
            border-left:4px solid #ef4444;margin:12px 0">
            <b style="color:#ef4444">Eliminar:</b>
            <span style="color:#e2e8f0"> {eq['nombre']}</span>
            <span style="color:#94a3b8"> · {eq['numero_serie']} · {eq['estado']}</span>
        </div>""", unsafe_allow_html=True)
        if st.checkbox(f"Confirmo eliminar **{eq['nombre']}**", key="conf_del_eq"):
            if st.button("🗑️ Eliminar definitivamente", type="primary"):
                r = api_delete(f"/equipos/{eq['id']}")
                if r.status_code == 204:
                    st.success("✅ Eliminado."); reload()
                else:
                    st.error(f"❌ Error {r.status_code}: {r.text}")

# ==============================================================================
# PÁGINA: DEPARTAMENTOS
# ==============================================================================
elif pagina == "🏢 Departamentos":
    st.markdown("## 🏢 Departamentos")
    tab_ver, tab_nuevo, tab_editar, tab_eliminar = st.tabs(
        ["📋 Ver todos", "➕ Agregar", "✏️ Editar", "🗑️ Eliminar"])

    # ── Ver ──
    with tab_ver:
        if not departamentos:
            st.info("Sin departamentos."); st.stop()
        eq_por_dep = {}
        for e in equipos:
            n = dep_map.get(e.get("departamento_id"), "Sin departamento")
            eq_por_dep[n] = eq_por_dep.get(n, 0) + 1

        cols = st.columns(min(len(departamentos), 3))
        for i, dep in enumerate(departamentos):
            cant = eq_por_dep.get(dep["nombre"], 0)
            with cols[i % 3]:
                st.markdown(f"""<div style="background:#1e293b;border-radius:12px;padding:20px;
                    border-left:4px solid #00d4ff;margin-bottom:16px">
                    <h4 style="color:#00d4ff;margin:0">{dep['nombre']}</h4>
                    <p style="color:#94a3b8;margin:4px 0">📍 {dep.get('ubicacion','—')}</p>
                    <p style="color:#e2e8f0;margin:8px 0 0 0">
                        <b style="color:#00d4ff;font-size:1.5rem">{cant}</b>
                        <span style="color:#94a3b8"> equipo(s)</span>
                    </p></div>""", unsafe_allow_html=True)

    # ── Nuevo ──
    with tab_nuevo:
        st.markdown("### Agregar nuevo departamento")
        with st.form("f_dep_nuevo", clear_on_submit=True):
            nombre   = st.text_input("Nombre del departamento *", placeholder="Finanzas")
            ubicacion = st.text_input("Ubicación", placeholder="Edificio A, Piso 3")
            if st.form_submit_button("💾 Agregar departamento", use_container_width=True):
                if not nombre:
                    st.error("❌ El nombre es obligatorio.")
                else:
                    r = api_post("/departamentos/", {"nombre": nombre, "ubicacion": ubicacion or None})
                    if r.status_code == 201:
                        st.success(f"✅ Departamento **{nombre}** creado."); reload()
                    elif r.status_code == 409:
                        st.error(f"❌ Ya existe un departamento llamado **{nombre}**.")
                    else:
                        st.error(f"❌ Error {r.status_code}: {r.text}")

    # ── Editar ──
    with tab_editar:
        st.markdown("### Editar departamento")
        if not departamentos:
            st.info("Sin departamentos."); st.stop()
        opts = {f"{d['id']} — {d['nombre']}": d for d in departamentos}
        sel  = st.selectbox("Selecciona departamento", list(opts.keys()), key="sel_edit_dep")
        dep  = opts[sel]
        with st.form("f_dep_edit"):
            new_nombre   = st.text_input("Nombre", value=dep["nombre"])
            new_ubicacion = st.text_input("Ubicación", value=dep.get("ubicacion") or "")
            if st.form_submit_button("💾 Guardar cambios", use_container_width=True):
                r = api_put(f"/departamentos/{dep['id']}",
                            {"nombre": new_nombre, "ubicacion": new_ubicacion or None})
                if r.status_code == 200:
                    st.success("✅ Departamento actualizado."); reload()
                else:
                    st.error(f"❌ Error {r.status_code}: {r.text}")

    # ── Eliminar ──
    with tab_eliminar:
        st.markdown("### Eliminar departamento")
        st.warning("⚠️ Los equipos de este departamento quedarán sin departamento asignado.")
        opts = {f"{d['id']} — {d['nombre']}": d for d in departamentos}
        sel  = st.selectbox("Selecciona departamento", list(opts.keys()), key="sel_del_dep")
        dep  = opts[sel]
        cant = sum(1 for e in equipos if e.get("departamento_id") == dep["id"])
        if cant > 0:
            st.info(f"ℹ️ Este departamento tiene **{cant}** equipo(s) asignado(s).")
        if st.checkbox(f"Confirmo eliminar **{dep['nombre']}**", key="conf_del_dep"):
            if st.button("🗑️ Eliminar departamento", type="primary"):
                r = api_delete(f"/departamentos/{dep['id']}")
                if r.status_code == 204:
                    st.success("✅ Departamento eliminado."); reload()
                else:
                    st.error(f"❌ Error {r.status_code}: {r.text}")

# ==============================================================================
# PÁGINA: ASIGNACIONES
# ==============================================================================
elif pagina == "👤 Asignaciones":
    st.markdown("## 👤 Asignaciones")
    tab_ver, tab_nuevo, tab_cerrar = st.tabs(
        ["📋 Ver activas", "➕ Nueva asignación", "✅ Cerrar / Editar"])

    # ── Ver ──
    with tab_ver:
        if not asignaciones:
            st.info("No hay asignaciones."); st.stop()
        df_a = pd.DataFrame(asignaciones)
        df_a["equipo"] = df_a["equipo_id"].map(eq_map).fillna("—")
        df_a["activa"] = df_a["fecha_devolucion"].isna()

        activas   = df_a[df_a["activa"]]
        cerradas  = df_a[~df_a["activa"]]

        c1, c2 = st.columns(2)
        c1.metric("Activas", len(activas))
        c2.metric("Cerradas", len(cerradas))

        st.markdown("### Asignaciones activas")
        if not activas.empty:
            st.dataframe(activas[["equipo","responsable","fecha_asignacion","notas"]].rename(columns={
                "equipo":"Equipo","responsable":"Responsable",
                "fecha_asignacion":"Desde","notas":"Notas"}),
                use_container_width=True, hide_index=True)
        else:
            st.info("No hay asignaciones activas.")

        if not cerradas.empty:
            with st.expander("Ver asignaciones cerradas"):
                st.dataframe(cerradas[["equipo","responsable","fecha_asignacion","fecha_devolucion"]].rename(
                    columns={"equipo":"Equipo","responsable":"Responsable",
                             "fecha_asignacion":"Desde","fecha_devolucion":"Hasta"}),
                    use_container_width=True, hide_index=True)

    # ── Nueva ──
    with tab_nuevo:
        st.markdown("### Registrar nueva asignación")
        if not equipos:
            st.warning("No hay equipos disponibles.")
        else:
            eq_libres = [e for e in equipos if e["estado"] != "asignado"]
            eq_todos  = equipos
            with st.form("f_asig_nuevo", clear_on_submit=True):
                eq_opts = {f"{e['id']} — {e['nombre']} ({e['estado']})": e for e in eq_todos}
                eq_sel  = st.selectbox("Equipo *", list(eq_opts.keys()))
                eq_id   = eq_opts[eq_sel]["id"]

                c1, c2 = st.columns(2)
                responsable = c1.text_input("Responsable *", placeholder="Ana Lucía Pérez")
                fecha_asig  = c2.date_input("Fecha de asignación")
                notas = st.text_area("Notas", placeholder="Descripción del motivo de asignación")

                if len(eq_libres) == 0:
                    st.warning("⚠️ Todos los equipos están asignados.")

                if st.form_submit_button("💾 Registrar asignación", use_container_width=True):
                    if not responsable:
                        st.error("❌ El responsable es obligatorio.")
                    else:
                        payload = {"equipo_id": eq_id, "responsable": responsable,
                                   "fecha_asignacion": str(fecha_asig), "notas": notas or None}
                        r = api_post("/asignaciones/", payload)
                        if r.status_code == 201:
                            st.success(f"✅ Asignación registrada para **{responsable}**.")
                            # Cambiar estado del equipo a "asignado"
                            api_put(f"/equipos/{eq_id}", {"estado": "asignado"})
                            reload()
                        else:
                            st.error(f"❌ Error {r.status_code}: {r.text}")

    # ── Cerrar / Editar ──
    with tab_cerrar:
        st.markdown("### Cerrar o editar una asignación")
        asig_activas = [a for a in asignaciones if not a.get("fecha_devolucion")]
        if not asig_activas:
            st.info("✅ No hay asignaciones activas abiertas.")
        else:
            opts = {f"ID {a['id']} — {eq_map.get(a['equipo_id'],'?')} → {a['responsable']}": a
                    for a in asig_activas}
            sel  = st.selectbox("Asignación activa", list(opts.keys()))
            asig = opts[sel]

            st.markdown(f"""<div style="background:#1e293b;border-radius:10px;padding:14px;
                border-left:4px solid #00d4ff;margin:12px 0">
                <b style="color:#00d4ff">Equipo:</b>
                <span style="color:#e2e8f0"> {eq_map.get(asig['equipo_id'],'—')}</span><br>
                <b style="color:#00d4ff">Responsable:</b>
                <span style="color:#e2e8f0"> {asig['responsable']}</span><br>
                <b style="color:#00d4ff">Desde:</b>
                <span style="color:#94a3b8"> {asig['fecha_asignacion']}</span>
            </div>""", unsafe_allow_html=True)

            with st.form("f_asig_editar"):
                new_resp  = st.text_input("Responsable", value=asig["responsable"])
                new_notas = st.text_area("Notas", value=asig.get("notas") or "")
                fecha_dev = st.date_input("Fecha de devolución (dejar vacío = mantener activa)",
                                          value=None)
                devolver  = st.checkbox("✅ Marcar como devuelto/cerrado")

                if st.form_submit_button("💾 Guardar", use_container_width=True):
                    payload = {"responsable": new_resp, "notas": new_notas or None,
                               "fecha_devolucion": str(fecha_dev) if devolver else None}
                    r = api_put(f"/asignaciones/{asig['id']}", payload)
                    if r.status_code == 200:
                        if devolver:
                            api_put(f"/equipos/{asig['equipo_id']}", {"estado": "bodega"})
                            st.success("✅ Asignación cerrada. Equipo regresó a bodega.")
                        else:
                            st.success("✅ Asignación actualizada.")
                        reload()
                    else:
                        st.error(f"❌ Error {r.status_code}: {r.text}")

# ==============================================================================
# PÁGINA: HISTORIAL AUDITORÍA
# ==============================================================================
elif pagina == "📋 Historial Auditoría":
    st.markdown("## 📋 Historial de Auditoría — Trigger SQL")
    st.info("💡 Historial generado **automáticamente** por el trigger `audit_cambio_estado` "
            "de PostgreSQL. Cada cambio de estado queda registrado sin intervención manual.")

    if not equipos:
        st.warning("Sin equipos."); st.stop()

    opts = {f"{e['id']} — {e['nombre']}": e["id"] for e in equipos}
    sel  = st.selectbox("Selecciona equipo", list(opts.keys()))
    eid  = opts[sel]

    try:
        hist = requests.get(f"{API_URL}/equipos/{eid}/historial", timeout=5).json()
    except:
        hist = []

    if not hist:
        st.success("✅ Sin cambios de estado registrados para este equipo.")
    else:
        st.markdown(f"**{len(hist)} cambio(s) registrados por el trigger**")
        colores = {"asignado":"#22c55e","bodega":"#3b82f6","mantenimiento":"#f59e0b"}
        for h in hist:
            ts  = h.get("cambiado_en","")[:19].replace("T"," ")
            ca  = colores.get(h["estado_anterior"],"#94a3b8")
            cn  = colores.get(h["estado_nuevo"],   "#94a3b8")
            st.markdown(f"""<div style="background:#1e293b;border-radius:10px;padding:16px;
                margin-bottom:10px;border-left:4px solid #00d4ff;display:flex;
                justify-content:space-between;align-items:center">
                <span style="background:{ca}22;color:{ca};padding:4px 12px;
                      border-radius:20px;font-weight:600">{h['estado_anterior']}</span>
                <span style="color:#64748b;margin:0 12px;font-size:1.2rem">→</span>
                <span style="background:{cn}22;color:{cn};padding:4px 12px;
                      border-radius:20px;font-weight:600">{h['estado_nuevo']}</span>
                <span style="color:#64748b;font-size:0.85rem;margin-left:auto">🕐 {ts}</span>
            </div>""", unsafe_allow_html=True)
