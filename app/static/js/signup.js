document.getElementById('signupForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const userType = document.getElementById('userType').value;
    const endpoint = userType === 'TRAINER' ? '/api/v1/users' : '/api/v1/members';

    const userData = {
        login_id: document.getElementById('loginId').value,
        email: document.getElementById('userEmail').value || null,
        password: document.getElementById('userPassword').value,
        name: document.getElementById('userName').value,
        birth_date: document.getElementById('birthDate').value,
        user_type: userType
    };

    // 회원(MEMBER)인 경우 추가 필드 설정
    if (userType === 'MEMBER') {
        Object.assign(userData, {
            gender: 'MALE',  // 기본값 설정
            contact: '000-000-0000',  // 기본값 설정
            fitness_goal: '체력 향상',  // 기본값 설정
            experience_level: 'BEGINNER',  // 기본값 설정
            has_injury: false,
            session_duration: 60,
            total_pt_count: 0,
            remaining_pt_count: 0
        });
    }

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });

        const data = await response.json();

        if (response.ok) {
            await Swal.fire({
                icon: 'success',
                title: '회원가입 성공!',
                text: '회원가입이 완료되었습니다.',
                confirmButtonText: '확인'
            });
            window.location.href = '/';
        } else {
            const errorMessage = data.detail || '회원가입 중 오류가 발생했습니다.';
            await Swal.fire({
                icon: 'error',
                title: '회원가입 실패',
                text: errorMessage,
                confirmButtonText: '확인'
            });
        }
    } catch (error) {
        console.error('Error:', error);
        await Swal.fire({
            icon: 'error',
            title: '서버 오류',
            text: '서버 연결 중 오류가 발생했습니다.',
            confirmButtonText: '확인'
        });
    }
}); 