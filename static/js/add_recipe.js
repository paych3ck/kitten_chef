function addIngredient() {
    const container = document.getElementById('ingredients');
    const newIngredient = document.createElement('div');
    newIngredient.classList.add('ingredient');
    newIngredient.innerHTML = `
        <br>
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
        <br>
        <input type="text" name="step_title" placeholder="Название этапа">
        <input type="number" name="timeAmount" class="numberInput" min="1" value="1">
        <select name="unit" class="unitDropdown">
            <option value="секунда">секунда</option>
            <option value="минута">минута</option>
            <option value="час">час</option>
        </select>
        <textarea name="step_description" placeholder="Описание"></textarea>
    `;
    container.appendChild(newStep);
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.numberInput').forEach((input) => {
        input.addEventListener('input', updateUnits);
    });

    document.querySelectorAll('.unitDropdown').forEach((dropdown) => {
        dropdown.addEventListener('change', updateUnits);
    });
});

function updateUnits() {
    const steps = document.querySelectorAll('.step');
    steps.forEach(step => {
        const numberInput = step.querySelector('.numberInput');
        const unitDropdown = step.querySelector('.unitDropdown');

        if (numberInput && unitDropdown) {
            const number = parseInt(numberInput.value);
            const unit = unitDropdown.value;

            unitDropdown.innerHTML = getUnitOptions(number, unit);
        }
    });
}

function getUnitOptions(number, currentUnit) {
    const units = {
        'секунда': ['секунда', 'секунды', 'секунд'],
        'минута': ['минута', 'минуты', 'минут'],
        'час': ['час', 'часа', 'часов']
    };

    let options = '';
    for (const [key, value] of Object.entries(units)) {
        const correctForm = getCorrectForm(number, value);
        options += `<option value="${key}" ${key === currentUnit ? 'selected' : ''}>${correctForm}</option>`;
    }
    return options;
}

function getCorrectForm(number, forms) {
    if (number % 10 === 1 && number % 100 !== 11) {
        return forms[0];
    } else if ([2, 3, 4].includes(number % 10) && ![12, 13, 14].includes(number % 100)) {
        return forms[1];
    } else {
        return forms[2];
    }
}
