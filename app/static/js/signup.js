document.getElementById('signupForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const userData = {
        email: document.getElementById('userEmail').value,
        password: document.getElementById('userPassword').value,
        name: document.getElementById('userName').value,
        birth_date: document.getElementById('birthDate').value,
        user_type: document.getElementById('userType').value
    };

    try {
        const response = await fetch('/api/v1/users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });

        if (response.ok) {
            await Swal.fire({
                icon: 'success',
                title: '회원가입 성공!',
                text: '회원가입이 완료되었습니다.',
                confirmButtonText: '확인'
            });
            window.location.href = '/';
        } else {
            const error = await response.json();
            await Swal.fire({
                icon: 'error',
                title: '회원가입 실패',
                text: error.detail || '회원가입 중 오류가 발생했습니다.',
                confirmButtonText: '확인'
            });
        }
    } catch (error) {
        await Swal.fire({
            icon: 'error',
            title: '서버 오류',
            text: '서버 연결 중 오류가 발생했습니다.',
            confirmButtonText: '확인'
        });
        console.error('Error:', error);
    }
}); 