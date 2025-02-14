document.getElementById('signupForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const userType = document.getElementById('userType').value.toLowerCase();
    const endpoint = userType === 'trainer' ? '/api/v1/users' : '/api/v1/members';

    // login_id에서 특수문자 제거
    const loginId = document.getElementById('loginId').value.replace(/[^a-zA-Z0-9]/g, '');
    
    if (loginId.length < 4) {
        await Swal.fire({
            icon: 'error',
            title: '입력 오류',
            text: '아이디는 최소 4자 이상의 영문자와 숫자만 사용 가능합니다.',
            confirmButtonText: '확인'
        });
        return;
    }

    // 생년월일 유효성 검사
    const birthDate = new Date(document.getElementById('birthDate').value);
    const today = new Date();
    if (birthDate > today) {
        await Swal.fire({
            icon: 'error',
            title: '입력 오류',
            text: '생년월일은 오늘 이후의 날짜일 수 없습니다.',
            confirmButtonText: '확인'
        });
        return;
    }

    const userData = {
        login_id: loginId,
        email: document.getElementById('userEmail').value || null,
        password: document.getElementById('userPassword').value,
        name: document.getElementById('userName').value,
        birth_date: document.getElementById('birthDate').value,
        user_type: userType
    };

    // 비밀번호 길이 체크
    if (userData.password.length < 8) {
        await Swal.fire({
            icon: 'error',
            title: '입력 오류',
            text: '비밀번호는 최소 8자 이상이어야 합니다.',
            confirmButtonText: '확인'
        });
        return;
    }

    // 회원(MEMBER)인 경우 추가 필드 설정
    if (userType === 'member') {
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

    console.log('Sending user data:', userData);  // 디버깅용 로그 추가

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });

        const data = await response.json();
        console.log('Server response:', JSON.stringify(data, null, 2));  // 더 자세한 로깅
        console.log('Response status:', response.status);

        if (response.ok) {
            await Swal.fire({
                icon: 'success',
                title: '회원가입 성공!',
                text: '회원가입이 완료되었습니다.',
                confirmButtonText: '확인'
            });
            window.location.href = '/';
        } else {
            // 상세한 에러 메시지 처리
            let errorMessage = '회원가입 중 오류가 발생했습니다.';
            if (data.detail) {
                if (Array.isArray(data.detail)) {
                    // 배열인 경우 각 에러 메시지를 줄바꿈으로 구분
                    errorMessage = data.detail.map(err => 
                        typeof err === 'object' ? JSON.stringify(err) : err
                    ).join('\n');
                } else if (typeof data.detail === 'object') {
                    // 객체인 경우 모든 에러 메시지를 표시
                    errorMessage = Object.values(data.detail).join('\n');
                } else {
                    errorMessage = data.detail;
                }
            }
            console.error('Error details:', JSON.stringify(data, null, 2));  // 더 자세한 에러 로깅
            
            await Swal.fire({
                icon: 'error',
                title: '회원가입 실패',
                text: errorMessage,
                html: errorMessage.replace(/\n/g, '<br>'),  // 줄바꿈을 HTML로 변환
                confirmButtonText: '확인'
            });
        }
    } catch (error) {
        console.error('Network or parsing error:', error);
        await Swal.fire({
            icon: 'error',
            title: '서버 오류',
            text: '서버 연결 중 오류가 발생했습니다.',
            confirmButtonText: '확인'
        });
    }
}); 