class ContentLoader {
    constructor() {
        this.content = null;
        this.apiUrl = 'https://zohp111iq5.execute-api.us-east-1.amazonaws.com/prod/registration';
    }

    async loadContent() {
        try {
            const response = await fetch('./content.json');
            this.content = await response.json();
            this.renderContent();
        } catch (error) {
            console.error('Error loading content:', error);
        }
    }

    renderContent() {
        if (!this.content) return;

        this.renderHero();
        this.renderAbout();
        this.renderSchedule();
        this.renderRegistration();
    }

    renderHero() {
        const hero = this.content.hero;
        
        document.getElementById('hero-tag').textContent = hero.tag;
        document.getElementById('hero-title').textContent = hero.title;
        document.getElementById('hero-description').textContent = hero.description;
        document.getElementById('hero-primary-btn').textContent = hero.primaryButton;
        document.getElementById('hero-secondary-btn').textContent = hero.secondaryButton;
        document.getElementById('participants-count').textContent = hero.stats.participants;
        document.getElementById('participants-label').textContent = hero.stats.participantsLabel;
        document.getElementById('days-count').textContent = hero.stats.days;
        document.getElementById('days-label').textContent = hero.stats.daysLabel;
    }

    renderAbout() {
        const about = this.content.about;
        
        document.getElementById('about-title').textContent = about.title;
        document.getElementById('about-subtitle').textContent = about.subtitle;
        document.getElementById('about-main-title').textContent = about.mainTitle;
        document.getElementById('about-description').textContent = about.description;

        const featuresGrid = document.getElementById('features-grid');
        featuresGrid.innerHTML = '';

        about.features.forEach(feature => {
            const featureDiv = document.createElement('div');
            featureDiv.className = 'feature';
            featureDiv.innerHTML = `
                <h4>${feature.title}</h4>
                <p>${feature.description}</p>
            `;
            featuresGrid.appendChild(featureDiv);
        });
    }

    renderSchedule() {
        const schedule = this.content.schedule;
        
        document.getElementById('schedule-title').textContent = schedule.title;
        document.getElementById('schedule-subtitle').textContent = schedule.subtitle;

        const scheduleContent = document.getElementById('schedule-content');
        scheduleContent.innerHTML = '';

        schedule.days.forEach(day => {
            const dayDiv = document.createElement('div');
            dayDiv.className = 'day-schedule';
            
            const sessionsHtml = day.sessions.map(session => `
                <div class="session">
                    <div class="session-time">${session.time}</div>
                    <div class="session-title">${session.title}</div>
                    ${session.speaker ? `<div class="session-speaker">${session.speaker}</div>` : ''}
                </div>
            `).join('');

            dayDiv.innerHTML = `
                <div class="day-header">
                    <h3>${day.day}</h3>
                    <p>${day.date}</p>
                </div>
                <div class="sessions">
                    ${sessionsHtml}
                </div>
            `;
            
            scheduleContent.appendChild(dayDiv);
        });
    }

    renderRegistration() {
        const registration = this.content.registration;
        
        document.getElementById('registration-title').textContent = registration.title;
        document.getElementById('registration-subtitle').textContent = registration.subtitle;
        document.getElementById('registration-price').textContent = registration.price;

        const includesList = document.getElementById('registration-includes');
        includesList.innerHTML = '';
        registration.includes.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            includesList.appendChild(li);
        });

        const formFields = document.getElementById('form-fields');
        formFields.innerHTML = '';
        
        registration.form.fields.forEach(field => {
            const formGroup = document.createElement('div');
            formGroup.className = 'form-group';
            
            if (field.type === 'select') {
                const options = field.options.map(option => 
                    `<option value="${option}">${option}</option>`
                ).join('');
                
                formGroup.innerHTML = `
                    <label for="${field.name}">${field.label}${field.required ? ' *' : ''}</label>
                    <select id="${field.name}" name="${field.name}" ${field.required ? 'required' : ''}>
                        <option value="">Selecione...</option>
                        ${options}
                    </select>
                `;
            } else {
                formGroup.innerHTML = `
                    <label for="${field.name}">${field.label}${field.required ? ' *' : ''}</label>
                    <input type="${field.type}" id="${field.name}" name="${field.name}" ${field.required ? 'required' : ''}>
                `;
            }
            
            formFields.appendChild(formGroup);
        });
    }

    async submitRegistration(formData) {
        try {
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();
            
            if (response.ok) {
                alert('Inscrição realizada com sucesso!');
                document.getElementById('registrationForm').reset();
            } else {
                alert(result.error || 'Erro ao realizar inscrição');
            }
        } catch (error) {
            console.error('Error submitting registration:', error);
            alert('Erro ao realizar inscrição. Tente novamente.');
        }
    }
}

const contentLoader = new ContentLoader();
document.addEventListener('DOMContentLoaded', () => {
    contentLoader.loadContent();
});
