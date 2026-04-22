# 🌍 Dashboard de Ciudades Mundiales
### Fundamentos de Inteligencia Artificial · IPN CECyT 9 Bátiz

---

## 📦 Instalación

Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
pip install customtkinter pandas matplotlib
```

---

## ▶ Cómo ejecutar

```bash
python dashboard.py
```

---

## 🔐 Credenciales de prueba

| Usuario  | Contraseña   | Rol    |
|----------|-------------|--------|
| admin    | admin123    | admin  |
| miriam   | batizcecyt9 | usuario|
| alumno   | ipn2024     | usuario|
| profesor | docente2024 | admin  |

Los usuarios se leen desde `usuarios.txt`. Puedes agregar más con el formato:
```
usuario:contraseña:Nombre Completo:rol
```

---

## 📊 Consultas incluidas (10)

| # | Consulta | Tipo de gráfica |
|---|----------|----------------|
| 1 | Top 10 ciudades más pobladas | Barras horizontales |
| 2 | Ciudades por continente | Pie + Barras |
| 3 | PIB per cápita por continente | Barras verticales |
| 4 | Temperatura vs Esperanza de vida | Dispersión (scatter) |
| 5 | Densidad poblacional Top 15 | Barras horizontales |
| 6 | Precipitación anual por región | Barras agrupadas |
| 7 | Alfabetización por continente | Barras horizontales |
| 8 | Ciudades más antiguas vs modernas | Barras dobles |
| 9 | Correlación PIB vs Esperanza de vida | Scatter + tendencia |
| 10 | Distribución de población mundial | Pie + Barras |

---

## 📁 Archivos

```
ai_dashboard/
├── dashboard.py     ← Programa principal
├── ciudades.csv     ← Dataset (50 ciudades, 14 variables)
├── usuarios.txt     ← Credenciales de acceso
└── README.md        ← Este archivo
```

---

## ✅ Características

- ✅ Login con lectura de usuario/contraseña desde archivo `.txt`
- ✅ Validación de campos (vacíos, longitud mínima, credenciales)
- ✅ Mostrar/ocultar contraseña
- ✅ Resultados en frame separado (sidebar + panel de resultados)
- ✅ Tablas interactivas con scroll para cada consulta
- ✅ 10 consultas complejas con pandas + matplotlib
- ✅ Tema oscuro con CustomTkinter
- ✅ 50 ciudades del mundo con 14 variables numéricas
