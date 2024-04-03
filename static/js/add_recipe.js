function addIngredient() {
    const container = document.getElementById('ingredients');
    const newIngredient = document.createElement('div');
    newIngredient.classList.add('ingredient');
    newIngredient.innerHTML = `
        <input type="text" name="ingredient_name" placeholder="Название ингредиента">
        <input type="text" name="ingredient_amount" placeholder="Количество">
    `;
    container.appendChild(newIngredient);
}

function addStep() {
    const container = document.getElementById('steps');
    const newStep = document.createElement('div');
    newStep.classList.add('step');
    newStep.innerHTML = `
        <input type="text" name="step_title" placeholder="Название этапа">
        <input type="text" name="step_duration" placeholder="Длительность">
        <textarea name="step_description" placeholder="Описание"></textarea>
    `;
    container.appendChild(newStep);
}
