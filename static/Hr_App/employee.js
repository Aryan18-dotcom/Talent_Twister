document.querySelectorAll('.Bar').forEach(bar => {
    const tooltip = bar.querySelector('.DaysLeft');
    const tooltipHeight = tooltip.offsetHeight;
    const tooltipWidth = tooltip.offsetWidth;
    
    // Show/hide tooltip
    bar.addEventListener('mouseenter', () => {
        gsap.to(tooltip, { 
            opacity: 1, 
            duration: 0.2 
        });
    });
    
    // Move tooltip with mouse (fully following cursor)
    bar.addEventListener('mousemove', (e) => {
        const barRect = bar.getBoundingClientRect();
        const mouseX = e.clientX - barRect.left;
        const mouseY = e.clientY - barRect.top;
        
        // Calculate centered position
        let tooltipX = mouseX - (tooltipWidth / 2);
        let tooltipY = mouseY - (tooltipHeight + 10); // 10px above cursor
        
        // Constrain X position
        if (tooltipX < 0) {
            tooltipX = 0;
        } else if (tooltipX + tooltipWidth > barRect.width) {
            tooltipX = barRect.width - tooltipWidth;
        }
        
        // Constrain Y position (keep above progress bar)
        const minY = -tooltipHeight - 5; // Max upward position
        const maxY = barRect.height - 5;  // Max downward position
        tooltipY = Math.max(minY, Math.min(tooltipY, maxY));
        
        gsap.to(tooltip, {
            left: tooltipX,
            top: tooltipY,
            duration: 0.1,
            ease: "power1.out"
        });
    });
    
    bar.addEventListener('mouseleave', () => {
        gsap.to(tooltip, { 
            opacity: 0, 
            duration: 0.2 
        });
    });
});







