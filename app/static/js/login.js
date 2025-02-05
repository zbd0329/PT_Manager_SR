document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    const userType = document.querySelector('input[name="user_type"]:checked').value;
    const formData = {
        login_id: document.getElementById('loginId').value,
        password: document.getElementById('userPassword').value,
        user_type: userType
    };

    console.log('로그인 시도:', { 
        login_id: formData.login_id, 
        user_type: userType 
    });

    try {
        // 사용자 유형에 따라 다른 엔드포인트 사용
        const endpoint = userType === 'trainer' 
            ? '/api/v1/users/login' 
            : '/api/v1/members/login';
            
        console.log('로그인 요청 엔드포인트:', endpoint);

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData),
            credentials: 'include'  // 쿠키를 포함하도록 설정
        });

        const data = await response.json();
        console.log('서버 응답:', data);

        if (response.ok) {
            // 로그인 성공
            localStorage.setItem('user_name', data.user_name);
            localStorage.setItem('user_type', data.user_type);

            console.log('저장된 사용자 정보:', {
                user_type: data.user_type,
                user_name: data.user_name
            });

            // 사용자 유형에 따라 리다이렉트
            const userType = data.user_type.toLowerCase();
            console.log('리다이렉트 결정을 위한 사용자 유형:', userType);

            if (userType === 'trainer') {
                console.log('트레이너 대시보드로 이동');
                window.location.href = '/trainer/dashboard';
            } else if (userType === 'member') {
                console.log('회원 대시보드로 이동');
                window.location.href = '/member/dashboard';
            } else {
                console.error('알 수 없는 사용자 유형:', userType);
                await Swal.fire({
                    icon: 'error',
                    title: '오류 발생',
                    text: '알 수 없는 사용자 유형입니다.',
                    confirmButtonText: '확인'
                });
            }
        } else {
            // 로그인 실패
            console.error('로그인 실패:', data);
            await Swal.fire({
                icon: 'error',
                title: '로그인 실패',
                text: data.detail || '로그인에 실패했습니다.',
                confirmButtonText: '확인'
            });
        }
    } catch (error) {
        console.error('로그인 오류:', error);
        await Swal.fire({
            icon: 'error',
            title: '서버 오류',
            text: '서버와의 통신 중 오류가 발생했습니다.',
            confirmButtonText: '확인'
        });
    }
}); 