# Candidatos para refactorizacion

Despues del ciclo TDD, buscar:

- **Duplicacion** → Extraer funcion/clase
- **Metodos largos** → Dividir en helpers privados (mantener tests en la interfaz publica)
- **Modulos superficiales** → Combinar o profundizar
- **Feature envy** → Mover logica a donde viven los datos
- **Obsesion por primitivos** → Introducir objetos de valor
- **Codigo existente** que el nuevo codigo revela como problematico
