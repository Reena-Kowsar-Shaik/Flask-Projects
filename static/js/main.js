// Apex Digital ATM - Interactive Features

document.addEventListener('DOMContentLoaded', () => {
  // 1. Live Terminal Clock
  const clockElement = document.getElementById('liveClock');
  if (clockElement) {
    const updateClock = () => {
      const now = new Date();
      const options = { 
        day: '2-digit', 
        month: 'short', 
        year: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit', 
        hour12: false 
      };
      clockElement.textContent = now.toLocaleDateString('en-GB', options).replace(/,/g, ' •');
    };
    updateClock();
    setInterval(updateClock, 1000);
  }

  // 2. Preset Amount Chips (Deposit & Withdraw)
  const presetChips = document.querySelectorAll('.preset-chip');
  const amountInput = document.getElementById('amountInput');
  if (amountInput && presetChips.length > 0) {
    presetChips.forEach(chip => {
      chip.addEventListener('click', () => {
        const value = chip.getAttribute('data-amount');
        if (value) {
          amountInput.value = value;
          amountInput.focus();
          
          // Visual bump
          amountInput.classList.add('pulse-highlight');
          setTimeout(() => amountInput.classList.remove('pulse-highlight'), 300);
        }
      });
    });
  }

  // 3. Demo Account Auto-Filler for Login Page
  const demoFillBtns = document.querySelectorAll('.js-demo-fill');
  const accInput = document.getElementById('accnum');
  const pinInput = document.getElementById('pin');
  if (demoFillBtns.length > 0 && accInput && pinInput) {
    demoFillBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const acc = btn.getAttribute('data-acc');
        const pin = btn.getAttribute('data-pin');
        if (acc && pin) {
          accInput.value = acc;
          pinInput.value = pin;
          accInput.focus();
        }
      });
    });
  }

  // 4. Interactive 3D Card Hover Effect
  const card = document.querySelector('.virtual-card');
  if (card) {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      
      const rotateX = ((y - centerY) / centerY) * -10;
      const rotateY = ((x - centerX) / centerX) * 10;
      
      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0)';
    });
  }
});
