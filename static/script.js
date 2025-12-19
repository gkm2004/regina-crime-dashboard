document.addEventListener('DOMContentLoaded', function () {
    const areaSelect = document.getElementById('areaSelect');
    console.log("Selected area:", this.value);
      
    
    // IMPORTANT: actually load charts package
    google.charts.load('current', { packages: ['corechart'] });
  
    google.charts.setOnLoadCallback(function () {
      // Draw initial chart
      updateCrimeTypePie(areaSelect.value);
  
      areaSelect.addEventListener('change', function () {
        const selected = this.value;
  
        // Update map
        fetch('/update-area', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ area: selected })
        })
        .then(response => response.text())
        .then(html => {
          document.querySelector('.map-container').innerHTML = html;
        })
        .catch(err => console.error("Map update failed:", err));
  
        // Update dynamic pie chart
        updateCrimeTypePie(selected);
      });
    });
  });
  
  function updateCrimeTypePie(area) {
    
    fetch('/get-pie-data', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ area })
    })
    .then(res => res.json())
    .then(data => {
      const el = document.getElementById('typePie');
  
      if (!data || data.length === 0) {
        el.innerHTML = "<p style='text-align:center;'>Select an area to see specific stats!</p>";
        return;
      }
  
      const chartData = [['Crime Type', 'Count'], ...data];
      const chart = new google.visualization.PieChart(el);
  
      chart.draw(
        google.visualization.arrayToDataTable(chartData),
        {
          title: `Crime Types in ${area}`,
          pieHole: 0.3,
          chartArea: { width: '90%', height: '80%' },
          legend: { position: 'right' }
        }
      );
    })
    .catch(err => console.error("Pie update failed:", err));
  }
  