// static/main.js
document.addEventListener('DOMContentLoaded', function() {
  const submitBtn = document.getElementById('submitBtn');
  const responseArea = document.getElementById('responseArea');

  submitBtn.addEventListener('click', async () => {
    responseArea.innerHTML = '';
    const payload = {
      age: parseInt(document.getElementById('age').value || '0'),
      gender: document.getElementById('gender').value || null,
      symptoms: {
        fever: document.getElementById('fever').value || 'none',
        abdominal_pain: document.getElementById('abdominal_pain').checked,
        coated_tongue: document.getElementById('coated_tongue').checked,
        severe_dehydration: document.getElementById('severe_dehydration').checked
      },
      tests: {
        blood_culture: document.getElementById('blood_culture').value || null
      },
      consent_store: document.getElementById('consent_store').checked
    };

    try {
      const res = await fetch('/api/submit', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) {
        responseArea.innerHTML = `<div class="card"><strong>Error:</strong> ${JSON.stringify(data)}</div>`;
        return;
      }
      renderResult(data);
    } catch (err) {
      responseArea.innerHTML = `<div class="card"><strong>Network error:</strong> ${err}</div>`;
    }
  });

  function renderResult(response) {
    const result = response.result;
    const severity = result.severity || 'unknown';
    let severityClass = '';
    if (severity === 'mild') severityClass = 'severity-mild';
    else if (severity === 'moderate') severityClass = 'severity-moderate';
    else if (severity === 'severe') severityClass = 'severity-severe';

    let treatmentsHtml = '';
    (result.treatments || []).forEach(t => {
      treatmentsHtml += `<li><strong>${t.med}</strong> ${t.dose ? `— ${t.dose}` : ''} ${t.duration_days ? `(${t.duration_days} days)` : ''}<br/><em>${t.notes || ''}</em></li>`;
    });

    let matched = (result.matched_rules || []).map(r => `${r.id}: ${r.name}`).join(', ') || 'none';

    responseArea.innerHTML = `
      <div class="card result ${severityClass}">
        <h3>Diagnosis: ${result.diagnosis_label}</h3>
        <p><strong>Severity:</strong> ${severity}</p>
        <p><strong>Matched rules:</strong> ${matched}</p>
        <h4>Recommended treatment(s):</h4>
        <ul>${treatmentsHtml}</ul>
        <p><small>Submission id: ${response.submission_id}</small></p>
      </div>
    `;
  }
});
