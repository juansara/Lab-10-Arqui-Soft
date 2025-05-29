# Lab-10-Arqui-Soft

ejecutar en local:
uvicorn poke_search.main:app --reload


validar funcionamiento:
curl -X POST http://localhost:8000/poke/search \
-H "Content-Type: application/json" \
-d '{"Pokemon_Name": "charizard"}'
