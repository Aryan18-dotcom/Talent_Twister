const avatarInput = document.getElementById('avatarInput');
const avatarImage = document.querySelectorAll('#avatarImage');
const avatarPlaceholder = document.querySelectorAll('#avatarPlaceholder');
const nameInput = document.getElementById('nameInput');
const usernameInput = document.getElementById('usernameInput');
const emailInput = document.getElementById('emailInput');
const passwordInput = document.getElementById('passwordInput');
const roleInput = document.getElementById('roleInput')
const saveProfileButton = document.getElementById('saveProfileButton');
const logoutButton = document.getElementById('logoutButton');
const profileName = document.querySelectorAll('#profileName');
const role = document.getElementById('role');
const userName = document.getElementById('Username');
const newTask = document.getElementById('newTask');
const myTaskContainer = document.getElementById('myTask');
let isProfileMenuOpen = false;

// localStorage.clear()

const mockData = {
    user: {
        name: 'Aryan Chheda',
        role: 'Senior Developer',
        avatar: null
    },
    stats: {
        tasksToday: 12,
        completedTasks: 48,
        ongoingProjects: 8,
        teamUpdates: 16
    },
    tasks: [
        {
            title: 'API Integration for Payment Gateway',
            description: 'Implement Stripe payment processing for the e-commerce platform',
            priority: 'high',
            priorityColor: 'bg-red-500/20 text-red-500', // High Priority Color
            dueDate: '2025-02-28',
            progress: 60,
            assignees: ['AT', 'JD'],
            assignedBy: 'Sarah Miller',
            assignedAt: '2025-02-24 09:30'
        },
        {
            title: 'User Dashboard Redesign',
            description: 'Create new wireframes and implement updated UI components',
            priority: 'medium',
            priorityColor: 'bg-yellow-500/20 text-yellow-500', // Medium Priority Color
            dueDate: '2025-03-05',
            progress: 35,
            assignees: ['AT', 'SL', 'RK'],
            assignedBy: 'Michael Chen',
            assignedAt: '2025-02-23 14:15'
        },
        {
            title: 'Database Optimization',
            description: 'Analyze and improve database query performance',
            priority: 'low',
            priorityColor: 'bg-green-500/20 text-green-500', // Low Priority Color
            dueDate: '2025-03-10',
            progress: 20,
            assignees: ['RK', 'SL'],
            assignedBy: 'Emma Davis',
            assignedAt: '2025-02-22 11:45'
        }
    ]
};



const tasks = [
    {
        title: "Database Optimization for Cloud Infrastructure",
        description: "Optimize database queries and implement caching mechanisms to improve system performance across cloud infrastructure.",
        assignedBy: "Admin",
        priority: "High Priority",
        priorityColor: "bg-red-500/20 text-red-500",
        dueDate: "Mar 15, 2025",
        assignedTime: "Assigned 5 mins ago"
    },
    {
        title: "UI/UX Enhancement for Dashboard",
        description: "Improve user experience by redesigning the dashboard layout and optimizing navigation elements.",
        assignedBy: "Project Manager",
        priority: "Medium Priority",
        priorityColor: "bg-yellow-500/20 text-yellow-500",
        dueDate: "Mar 20, 2025",
        assignedTime: "Assigned 1 hour ago"
    },
    {
        title: "Security Audit for Web Application",
        description: "Conduct a security audit to identify vulnerabilities and implement necessary fixes to improve security.",
        assignedBy: "Security Team",
        priority: "Critical Priority",
        priorityColor: "bg-red-700/20 text-red-700",
        dueDate: "Mar 10, 2025",
        assignedTime: "Assigned 2 days ago"
    }
];



function generalFunctions() {
    document.querySelector('button.bg-primary').addEventListener('click', acceptTask);

    document.querySelectorAll('.task-card').forEach(card => {
        card.addEventListener('click', () => {
            card.style.transform = 'scale(0.98)';
            setTimeout(() => {
                card.style.transform = '';
            }, 100);
        });
    });
    document.querySelectorAll('nav button').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('nav button').forEach(b => {
                b.classList.remove('text-primary');
                b.classList.add('text-gray-400');
            });
            btn.classList.remove('text-gray-400');
            btn.classList.add('text-primary');
        });
    });
}
generalFunctions()


avatarInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const imageUrl = e.target.result;
            avatarImage.forEach(e => {
                e.src = imageUrl;
                e.classList.remove('hidden');
            })
            avatarPlaceholder.forEach(e => {
                e.classList.add('hidden');
            })
        };
        reader.readAsDataURL(file);
    }
});


saveProfileButton.addEventListener('click', () => {
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded shadow-lg z-50';
    notification.textContent = 'Profile updated successfully';
    document.body.appendChild(notification);

    // profileName.textContent = nameInput.value;
    profileName.forEach(e => {
        e.textContent = nameInput.value
    })
    role.textContent = roleInput.value;

    setTimeout(() => {
        notification.remove();
    }, 2000);
});

function customAlert(message, callback = null) {
    const overlay = document.createElement('div');
    overlay.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';

    const alertBox = document.createElement('div');
    alertBox.className = 'bg-white text-black p-6 rounded-lg shadow-lg text-center w-80';

    const messageText = document.createElement('p');
    messageText.textContent = message;
    alertBox.appendChild(messageText);

    const okButton = document.createElement('button');
    okButton.textContent = 'OK';
    okButton.className = 'mt-4 bg-blue-500 border-none text-white px-6 py-2 rounded shadow';

    function closeAlert() {
        overlay.remove();
        document.removeEventListener('keydown', handleEnterKey); 
        if (callback) callback(); 
    }

    function handleEnterKey(event) {
        if (event.key === "Enter") {
            closeAlert();
        }
    }

    document.addEventListener('keydown', handleEnterKey);

    okButton.onclick = closeAlert;

    alertBox.appendChild(okButton);
    overlay.appendChild(alertBox);
    document.body.appendChild(overlay);

    okButton.focus();
}

function openPanel(id) {
    document.getElementById(id).classList.remove('translate-x-full', 'hidden');
}
function closePanel(id) {
    document.getElementById(id).classList.add('translate-x-full', 'hidden');
}
function openSection(sectionId) {
    document.getElementById(sectionId).classList.remove('translate-x-full', 'hidden')
}
function closeSetting(sectionId) {
    document.getElementById(sectionId).classList.add('translate-x-full', 'hidden')
}


function mockDataMyTask() {
    myTaskContainer.innerHTML = "";

    mockData.tasks.forEach(tasks => {
        const randomValue = Math.floor(Math.random() * 101); // Random progress between 0-100
        const randomCount = randomValue >= 50 ? 2 : 3; // If randomValue >= 50, show 2 assignees, else 3
        const selectedAssignees = tasks.assignees.slice(0, randomCount);

        // Generate assignee divs dynamically
        const assigneeHTML = selectedAssignees.map(assignee => `
            <div class="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center">${assignee}</div>
        `).join('');

        const html = `
            <div class="task-card bg-gray-700 p-4 rounded-lg">
                <div class="flex items-center justify-between">
                    <div>
                        <h3 class="font-medium">${tasks.title}</h3>
                        <p class="text-sm text-gray-400 mt-1">${tasks.description}</p>
                        <p class="text-xs text-gray-500 mt-1">Assigned to Sarah Miller on Feb 24, 2025</p>
                    </div>
                    <span class="px-2 py-1 text-xs rounded-full ${tasks.priorityColor}">${tasks.priority}</span>
                </div>
                <div class="mt-4">
                    <div class="flex items-center justify-between text-sm text-gray-400">
                        <div class="flex items-center space-x-2">
                            <i class="ri-calendar-line"></i>
                            <span>Due ${tasks.dueDate}</span>
                        </div>
                        <div class="flex -space-x-2">
                            ${assigneeHTML}
                        </div>
                    </div>
                    <div class="mt-3 bg-gray-600 rounded-full h-2">
                        <div class="bg-primary h-2 rounded-full" style="width: ${randomValue}%"></div>
                    </div>
                </div>
            </div>
        `;
        myTaskContainer.innerHTML += html;
    });
}
// mockDataMyTask();


function acceptTask(index) {
    const task = tasks[index];

    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded shadow-lg';
    notification.textContent = 'Task accepted successfully';
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);

    const taskCard = document.createElement('div');
    taskCard.className = 'task-card bg-gray-700 p-4 rounded-lg';
    taskCard.innerHTML = `
        <div class="flex items-center justify-between">
            <div>
                <h3 class="font-medium">${task.title}</h3>
                <p class="text-sm text-gray-400 mt-1">${task.description}</p>
                <p class="text-xs text-gray-500 mt-1">Assigned by ${task.assignedBy} on ${new Date().toLocaleDateString()}</p>
            </div>
            <span class="px-2 py-1 text-xs rounded-full ${task.priorityColor}">${task.priority}</span>
        </div>
        <div class="mt-4">
            <div class="flex items-center justify-between text-sm text-gray-400">
                <div class="flex items-center space-x-2">
                    <i class="ri-calendar-line"></i>
                    <span>Due ${task.dueDate}</span>
                </div>
                <div class="flex -space-x-2">
                    <div class="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center">AT</div>
                </div>
            </div>
            <div class="mt-3 bg-gray-600 rounded-full h-2">
                <div class="bg-primary h-2 rounded-full" style="width: 0%"></div>
            </div>
        </div>
    `;

    myTaskContainer.insertBefore(taskCard, myTaskContainer.firstChild);

    const taskElements = newTask.querySelectorAll(".task-card");

    taskElements.forEach((taskElement) => {
        if (parseInt(taskElement.getAttribute("data-index")) === index) {
            taskElement.remove();
        }
    });

    if (newTask.children.length === 0) {
        newTask.innerHTML = `
            <div class="task-card bg-gray-700 width-full py-14 rounded-lg mb-6">
                <div class="text-gray-400 text-center">
                    <i class="ri-checkbox-circle-line text-4xl mb-2"></i>
                    <p>No new tasks available from admin</p>
                </div>
            </div>
        `;
    }
}





// const isLoggedIn = localStorage.getItem('isLoggedIn');
// const userType = localStorage.getItem('userType');
// console.log(isLoggedIn, userType);

// if (isLoggedIn !== 'true' || userType !== 'admin') {
//     customAlert('Session expired. Please log in again.', () => {
//         window.location.href = 'login.html'; 
//     });   
// } else {
//     const logoutButton = document.querySelector('.logout');
//     if (logoutButton) {
//         function logoutUser() {
//             const notification = document.createElement('div');
//             notification.className = 'fixed top-4 right-1/2 translate-x-1/2 bg-red-500 text-white px-6 py-3 rounded shadow-lg';
//             notification.textContent = 'Logout successful. See you again soon!';
//             document.body.appendChild(notification);
//             setTimeout(() => {
//                 notification.remove();
//                 localStorage.removeItem('isLoggedIn');
//                 localStorage.removeItem('userType');
//                 window.location.href = 'login.html';
//             }, 1000);
//         }
//     }
// }

// window.onpageshow = function (event) {
//     if (event.persisted) {
//         window.location.href = 'login.html';
//     }
// };


function quickTask(site){
    window.location.href = `/NevigateSite/${site}.html`
}