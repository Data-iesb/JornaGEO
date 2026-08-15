class ContentLoader {
    constructor() {
        this.content = null;
        this.apiUrl = 'https://a4ax2vyqte.execute-api.us-east-1.amazonaws.com/prod/register';
    }

    async loadContent() {
        try {
            const response = await fetch(`./content.json?v=${Date.now()}`, {
                cache: 'no-cache',
                headers: {
                    'Cache-Control': 'no-cache'
                }
            });
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
        this.renderCoordination();
    }

    renderHero() {
        const hero = this.content.hero;
        
        document.getElementById('hero-tag').innerHTML = hero.tag;
        document.getElementById('hero-title').innerHTML = hero.title;
        document.getElementById('hero-description').innerHTML = hero.description;
        document.getElementById('hero-primary-btn').innerHTML = hero.primaryButton;
        document.getElementById('hero-secondary-btn').innerHTML = hero.secondaryButton;
        document.getElementById('participants-count').innerHTML = hero.stats.participants;
        document.getElementById('participants-label').innerHTML = hero.stats.participantsLabel;
        document.getElementById('days-count').innerHTML = hero.stats.days;
        document.getElementById('days-label').innerHTML = hero.stats.daysLabel;
    }

    renderAbout() {
        const about = this.content.about;
        
        document.getElementById('about-title').innerHTML = about.title;
        document.getElementById('about-subtitle').innerHTML = about.subtitle;
        document.getElementById('about-main-title').innerHTML = about.mainTitle;
        document.getElementById('about-description').innerHTML = about.description;

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
        
        document.getElementById('schedule-title').innerHTML = schedule.title;
        document.getElementById('schedule-subtitle').innerHTML = schedule.subtitle;

        const scheduleContent = document.getElementById('schedule-content');
        scheduleContent.innerHTML = '';

        schedule.days.forEach(day => {
            const dayDiv = document.createElement('div');
            dayDiv.className = 'day-schedule';
            
            const sessionsHtml = day.sessions.map(session => `
                <div class="session">
                    <div class="session-time">${session.time}</div>
                    <div class="session-title">${session.title}</div>
                    ${session.speaker ? `
                        <div class="session-speaker">
                            ${session.speakers ? `
                                ${session.speakers.map(speaker => `
                                    <div class="speaker-info">
                                        <img src="${speaker.photo}" alt="${speaker.name}" class="speaker-photo">
                                        <div class="speaker-details">
                                            <div class="speaker-name">${speaker.name}</div>
                                            <div class="speaker-links">
                                                ${speaker.lattes ? `<a href="${speaker.lattes}" target="_blank">Currículo Lattes</a>` : ''}
                                                ${speaker.linkedin ? `<a href="${speaker.linkedin}" target="_blank">LinkedIn</a>` : ''}
                                            </div>
                                        </div>
                                    </div>
                                `).join('')}
                            ` : session.speakerInfo ? `
                                <div class="speaker-info">
                                    <img src="${session.speakerInfo.photo}" alt="${session.speaker}" class="speaker-photo">
                                    <div class="speaker-details">
                                        <div class="speaker-name">${session.speaker}</div>
                                        <div class="speaker-links">
                                            <a href="${session.speakerInfo.lattes}" target="_blank">Currículo Lattes</a>
                                            <a href="${session.speakerInfo.linkedin}" target="_blank">LinkedIn</a>
                                        </div>
                                    </div>
                                </div>
                            ` : session.speaker}
                        </div>
                    ` : ''}
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
        
        document.getElementById('registration-title').innerHTML = registration.title;
        document.getElementById('registration-subtitle').innerHTML = registration.subtitle;
        document.getElementById('registration-price').innerHTML = registration.price;

        const includesList = document.getElementById('registration-includes');
        includesList.innerHTML = '';
        registration.includes.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = item;
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
            } else if (field.type === 'checkbox') {
                formGroup.innerHTML = `
                    <div class="checkbox-group">
                        <input type="checkbox" id="${field.name}" name="${field.name}" value="sim">
                        <label for="${field.name}">${field.label}</label>
                    </div>
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

    renderCoordination() {
        const coordination = this.content.coordination;
        if (!coordination) return;
        
        document.getElementById('coordination-title').innerHTML = coordination.title;
        
        const coordinationContent = document.getElementById('coordination-content');
        coordinationContent.innerHTML = '';
        
        let currentSection = '';
        let currentGrid = null;
        
        coordination.coordinators.forEach(coordinator => {
            if (coordinator.section !== currentSection) {
                currentSection = coordinator.section;
                const sectionHeader = document.createElement('div');
                sectionHeader.className = 'coordination-section';
                sectionHeader.innerHTML = `<h3>${coordinator.section}</h3>`;
                coordinationContent.appendChild(sectionHeader);
                
                currentGrid = document.createElement('div');
                currentGrid.className = 'coordination-grid';
                coordinationContent.appendChild(currentGrid);
            }
            
            const coordinatorCard = document.createElement('div');
            coordinatorCard.className = 'coordinator-card';
            
            const linkedinLink = coordinator.linkedin ? 
                `<a href="${coordinator.linkedin}" target="_blank" class="link-btn">LinkedIn</a>` : '';
            
            const websiteLink = coordinator.website ? 
                `<a href="${coordinator.website}" target="_blank" class="link-btn">Website</a>` : '';
            
            const phoneInfo = coordinator.phone ? 
                `<div class="coordinator-phone">Telefone: ${coordinator.phone}</div>` : '';
            
            coordinatorCard.innerHTML = `
                <div class="coordinator-photo">
                    <img src="${coordinator.photo}" alt="${coordinator.name}">
                </div>
                <div class="coordinator-info">
                    <h4>${coordinator.name}</h4>
                    <div class="coordinator-links">
                        <a href="${coordinator.lattes}" target="_blank" class="link-btn">Lattes</a>
                        ${linkedinLink}
                        ${websiteLink}
                    </div>
                    ${phoneInfo}
                </div>
            `;
            
            currentGrid.appendChild(coordinatorCard);
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
                alert('Inscrição realizada com sucesso! Verifique seu e-mail para um "AWS Notification - Subscription Confirmation" e confirme sua inscrição.');
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
