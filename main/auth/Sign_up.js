document.getElementById('signupform').addEventListener('submit', async function(e) {
  e.preventDefault();
  const email = document.getElementById('mail').value;
  const password = document.getElementById('password').value;
  const name = document.getElementById('username').value;

  try {
    const res = await fetch('/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, name })
    });
    const data = await res.json();
    alert(data.message);
    if (res.ok) {
      window.location.href = 'top.html';
    }
  } catch (err) {
    alert('通信エラー');
    console.error(err);
  }
});