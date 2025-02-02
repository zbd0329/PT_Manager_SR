document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const userType = document.getElementById('userType').value;
    console.log('Selected user type:', userType); // 디버깅용 로그

    const loginData = {
        id: document.getElementById('userId').value,
        password: document.getElementById('userPassword').value,
        user_type: userType
    };

    console.log('Login data:', loginData); // 디버깅용 로그

    try {
        const response = await fetch('/users/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(loginData)
        });

        if (response.ok) {
            const data = await response.json();
            // JWT 토큰과 사용자 정보 저장
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('userName', data.user_name);
            localStorage.setItem('userType', data.user_type);
            
            await Swal.fire({
                icon: 'success',
                title: '로그인 성공!',
                text: '로그인하였습니다.',
                confirmButtonText: '확인'
            });

            // 사용자 유형에 따라 다른 대시보드로 리다이렉트
            if (data.user_type === 'trainer') {
                window.location.href = '/trainer/dashboard';
            } else {
                window.location.href = '/member/dashboard';
            }
        } else {
            const error = await response.json();
            await Swal.fire({
                icon: 'error',
                title: '로그인 실패',
                text: error.detail || '로그인 중 오류가 발생했습니다.',
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