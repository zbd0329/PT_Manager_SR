document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const userType = document.querySelector('input[name="user_type"]:checked').value;
    const loginId = document.getElementById('loginId').value;
    console.log('Login attempt:', { login_id: loginId, type: userType }); // 디버깅용 로그

    const loginData = {
        login_id: loginId,
        password: document.getElementById('userPassword').value,
        user_type: userType
    };

    const API_URL = '/api/v1/users/login';
    console.log('Sending request to:', API_URL); // 디버깅용 로그
    console.log('Login data:', loginData); // 디버깅용 로그

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(loginData)
        });

        console.log('Response status:', response.status); // 디버깅용 로그

        let data;
        try {
            const textData = await response.text();
            console.log('Raw response:', textData); // 디버깅용 로그
            data = textData ? JSON.parse(textData) : {};
        } catch (e) {
            console.error('JSON parsing error:', e);
            data = {};
        }

        if (response.ok) {
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
            let errorMessage = '로그인 중 오류가 발생했습니다.';
            
            if (response.status === 401) {
                errorMessage = '아이디, 비밀번호 또는 사용자 유형이 올바르지 않습니다.';
            } else if (response.status === 404) {
                errorMessage = '로그인 서비스를 찾을 수 없습니다. 잠시 후 다시 시도해주세요.';
            } else if (data.detail) {
                errorMessage = data.detail;
            }

            console.error('Login failed:', {
                status: response.status,
                data: data
            });

            await Swal.fire({
                icon: 'error',
                title: '로그인 실패',
                text: errorMessage,
                confirmButtonText: '확인'
            });
        }
    } catch (error) {
        console.error('Network error:', error);
        await Swal.fire({
            icon: 'error',
            title: '서버 오류',
            text: '서버 연결 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.',
            confirmButtonText: '확인'
        });
    }
}); 