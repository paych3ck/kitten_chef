function addIngredient() {
    const container = document.getElementById('ingredients');
    const newIngredient = document.createElement('div');
    newIngredient.classList.add('ingredient');
    newIngredient.innerHTML = `
        <br>
        <input type="text" name="ingredient_name" placeholder="Название ингредиента" required>
        <input type="text" name="ingredient_amount" placeholder="Количество" required>
    `;
    container.appendChild(newIngredient);
}

function addStep() {
    const container = document.getElementById('steps');
    const stepCount = document.querySelectorAll('.step').length + 1;
    const newStep = document.createElement('div');
    newStep.classList.add('step');
    newStep.innerHTML = `
        <br>
        <input type="text" name="step_title" placeholder="Название этапа" required>
        <input type="number" name="timeAmount" class="numberInput" min="1" value="1" required>
        <select name="unit" class="unitDropdown" required>
            <option value="секунда">секунда</option>
            <option value="минута">минута</option>
            <option value="час">час</option>
        </select>
        <input type="hidden" name="unit_text" class="unit_text">
        <textarea name="step_description" placeholder="Описание" required></textarea>
    `;
    container.appendChild(newStep);

    newStep.querySelector('.numberInput').addEventListener('input', updateUnits);
    newStep.querySelector('.unitDropdown').addEventListener('change', updateUnits);

    updateUnits();
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
        const unitTextField = step.querySelector('.unit_text');
        const unitText = unitDropdown.options[unitDropdown.selectedIndex].textContent;

        if (numberInput && unitDropdown) {
            const number = parseInt(numberInput.value);
            const currentUnit = unitDropdown.value;

            const unitOptions = getUnitOptions(number, currentUnit);
            unitDropdown.innerHTML = unitOptions;
            unitDropdown.value = currentUnit;
            unitTextField.value = unitText;
        }
    });
}

const units = {
    'секунда': ['секунда', 'секунды', 'секунд'],
    'минута': ['минута', 'минуты', 'минут'],
    'час': ['час', 'часа', 'часов']
};

function getUnitOptions(number, currentUnit) {
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
