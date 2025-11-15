from __init__ import create_app, db
from models.factura import Factura
from models.user import User

app = create_app()

# === CREAR TABLAS AL ARRANQUE ===
with app.app_context():
    db.create_all()  # Crea User y Factura si no existen
    print("✅ Base de datos inicializada – tablas User y Factura creadas")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
