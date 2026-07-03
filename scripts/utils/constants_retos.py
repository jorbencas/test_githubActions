import os

CONFIG = {
    "GEMINI_KEY": os.getenv("GEMINI_API_KEY"),
    "AI_MODELS": ["gemini-2.5-flash", "gemini-2.5-pro"],
    "IMAGE_MODELS": ["imagen-3.0-generate-002"],
    "CHALLENGES_DIR": "../src/content/auto-challenges",
    "DEFAULT_LANG": "Python",
    "IMAGES_FOLDER": "../public/img/retos",
    "IMAGES_PATH_PREFIX": "/img/retos",
}

WEBS_RETOS = {
    "Retos de Programación": {"url": "https://retosdeprogramacion.com/ejercicios/", "selector": "a[href*='/retos/']"},
    "Codewars": {"url": "https://www.codewars.com/kata/latest", "selector": ".item-title a"},
    "RetosMoure": {"url": "https://retosdeprogramacion.com/semanales2024", "selector": "a[href*='/retos/']"}
}

RETO_MD_TEMPLATE = """---
draft: false
title: "🏆 RETO: {titulo}"
description: "{resumen_corto}"
pubDate: "{fecha_pub}"
tags: {tags_seo}
slug: "{slug_name}"
image: "{ruta_imagen}"
author: "Jorge Beneyto Castelló"
difficulty: "{dificultad}"
languages: ["python", "javascript", "java", "typescript"]
---

import Challenge from '@components/Challenge.astro';
import CodeTabs from '@components/CodeTabs.svelte';

# 🎯 Desafío: {titulo}

### 📝 Descripción del Reto
{descripcion_ia}

<Challenge 
  nivel="{dificultad}" 
  mision="{resumen_corto}" 
/>

---

### 🧪 Casos de Prueba

| Entrada | Salida esperada |
|---------|-----------------|
{tabla_casos}

---

## 💡 Guía de Solución Paso a Paso

<details>
<summary><b>Ver explicación y código 🛠️ (¡No hagas spoiler!)</b></summary>
<div class="details-content">

### 🏗️ Paso 1: Análisis de la lógica
{paso_1}

### ⚙️ Paso 2: Implementación
{paso_2}

{paso_3}

**Complejidad temporal:** {big_o_time}  
**Complejidad espacial:** {big_o_space}  

### 💻 Código de la Solución

<CodeTabs client:load>

```python
{python_code}
```

```javascript
{javascript_code}
```

```java
{java_code}
```

```typescript
{typescript_code}
```

</CodeTabs>

</div>
</details>
"""

PROMPT_IMAGEN_TEMPLATE_RETO = """
Minimalist tech illustration of {titulo_post}. 
Style: Flat vector art, isometric perspective, cyberpunk aesthetics. 
Palette: Deep slate background, neon cyan and electric blue highlights. 
Clean lines, high contrast, professional digital art, centered composition. 
No text, no faces, simple geometric shapes.
"""
