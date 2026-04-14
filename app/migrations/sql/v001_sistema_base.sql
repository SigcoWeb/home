-- v001: índices y datos iniciales del sistema sigcoweb

CREATE INDEX IF NOT EXISTS idx_sgc_empresas_ruc ON sgc_sys_empresas(ruc);
CREATE INDEX IF NOT EXISTS idx_sgc_licencias_clave ON sgc_sys_licencias(clave_licencia);

-- Superadmin de Walter — CAMBIAR CLAVE antes de producción
INSERT INTO sgc_sys_usuarios_master (email, clave_hash, nombre, activo, es_superadmin, id_empresa)
VALUES (
    'admin@sigcoweb.com',
    '$2b$12$placeholder_cambiar_en_produccion',
    'Administrador sigcoWeb',
    true,
    true,
    NULL
) ON CONFLICT (email) DO NOTHING;
