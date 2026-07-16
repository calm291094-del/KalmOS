"""Generador de archivos PAC (Proxy Auto-Configuration)"""
from pathlib import Path
from system.config import BASE_DIR, DATA_DIR, PROXY_PORT, log


class PACGenerator:
    PAC_DIR = DATA_DIR / "pac"
    
    @staticmethod
    def init():
        PACGenerator.PAC_DIR.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def generate_pac(proxy_host="127.0.0.1", proxy_port=None, custom_rules=None):
        """
        Genera un archivo PAC que redirige dominios específicos al proxy de Kalm.
        """
        if proxy_port is None:
            proxy_port = PROXY_PORT
        
        PACGenerator.init()
        
        # Obtener reglas del proxy
        from system.registry import get_proxy_server
        proxy = get_proxy_server()
        rules = proxy.get_rules() if proxy else {}
        
        if custom_rules:
            rules.update(custom_rules)
        
        # Construir función FindProxyForURL
        pac_content = f'''// ═══════════════════════════════════════════════════════════
// KALM OS v4.2 - Proxy Auto-Configuration (PAC)
// Generado automáticamente - No editar
// ═══════════════════════════════════════════════════════════

function FindProxyForURL(url, host) {{
    // Lista de dominios gestionados por Kalm OS
    var kalmDomains = [
'''
        # Agregar dominios
        for domain in rules.keys():
            pac_content += f'        "{domain}",\n'
        
        pac_content += f'''    ];
    
    // Proxy de Kalm OS
    var KALM_PROXY = "PROXY {proxy_host}:{proxy_port}; DIRECT";
    
    // Verificar si el host coincide con algún dominio de Kalm
    host = host.toLowerCase();
    
    for (var i = 0; i < kalmDomains.length; i++) {{
        var domain = kalmDomains[i].toLowerCase();
        
        // Coincidencia exacta
        if (host === domain) {{
            return KALM_PROXY;
        }}
        
        // Coincidencia de subdominio (*.domain)
        if (host.endsWith("." + domain)) {{
            return KALM_PROXY;
        }}
    }}
    
    // Dominios locales adicionales
    if (
        host.endsWith(".local") ||
        host.endsWith(".kalm") ||
        host === "localhost" ||
        host.startsWith("127.")
    ) {{
        return KALM_PROXY;
    }}
    
    // Todo lo demás: conexión directa
    return "DIRECT";
}}
'''
        
        # Guardar archivo PAC
        pac_file = PACGenerator.PAC_DIR / "kalm_proxy.pac"
        pac_file.write_text(pac_content, encoding="utf-8")
        
        # También generar versión con todos los dominios del DNS
        try:
            from system.registry import get_dns_server
            dns = get_dns_server()
            if dns:
                dns_rules = dns.get_rules()
                all_domains = set(rules.keys()) | set(dns_rules.keys())
                
                pac_full = pac_content.replace(
                    'var kalmDomains = [',
                    'var kalmDomains = [\n' + '\n'.join([f'        "{d}",' for d in all_domains])
                )
                
                pac_full_file = PACGenerator.PAC_DIR / "kalm_proxy_full.pac"
                pac_full_file.write_text(pac_full, encoding="utf-8")
        except Exception as e:
            log(f"⚠️ Error generando PAC completo: {e}", "WARN")
        
        log(f"📄 PAC generado: {pac_file}")
        return str(pac_file)
    
    @staticmethod
    def get_pac_url():
        """Retorna la URL para acceder al archivo PAC desde el navegador"""
        from system.config import UI_PORT
        return f"http://127.0.0.1:{UI_PORT}/static/pac/kalm_proxy.pac"
    
    @staticmethod
    def get_browser_config_instructions():
        """Instrucciones para configurar navegadores"""
        pac_url = PACGenerator.get_pac_url()
        return {
            "firefox": {
                "steps": [
                    "Abrir Firefox → Configuración → General",
                    "Buscar 'Configuración de red' → 'Configuración...'",
                    "Seleccionar 'URL de configuración proxy automática'",
                    f"Pegar: {pac_url}",
                    "Guardar"
                ]
            },
            "chrome": {
                "steps": [
                    "Abrir Chrome → Configuración → Sistema",
                    "Click en 'Abrir configuración de proxy de tu computadora'",
                    "En Windows: pestaña 'Conexiones' → 'Configuración LAN'",
                    "Marcar 'Usar script de configuración automática'",
                    f"Pegar: {pac_url}",
                    "Guardar"
                ]
            },
            "edge": {
                "steps": [
                    "Abrir Edge → Configuración → Sistema y rendimiento",
                    "Abrir configuración de proxy del sistema",
                    "Marcar 'Usar script de configuración automática'",
                    f"Pegar: {pac_url}",
                    "Guardar"
                ]
            }
        }