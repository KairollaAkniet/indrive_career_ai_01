import sqlite3
conn = sqlite3.connect('candidates.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE candidates ADD COLUMN ai_probability INTEGER DEFAULT 0")
    conn.commit()
    print("✅ ai_probability бағаны сәтті қосылды!")
except sqlite3.OperationalError:
    print("⚠️ Баған қазірдің өзінде бар немесе база табылмады.")
finally:
    conn.close()