export const PREDICTIONS = [
    {
        id: 101, name: '단백질 디저트', cat: 'food', prob: 84, score: 82,
        analysis: '고단백 간식과 저당 디저트 관심이 함께 상승하고 있어 편의점, 카페, 홈트 소비층으로 확산 가능성이 높습니다.'
    },
    {
        id: 102, name: 'AI 쇼핑비서', cat: 'technology', prob: 79, score: 77,
        analysis: '가격 비교, 사이즈 추천, 리뷰 요약 기능이 커머스 앱에 빠르게 붙으면서 개인화 쇼핑 도우미 수요가 커지고 있습니다.'
    },
    {
        id: 103, name: '로컬 러닝크루', cat: 'lifestyle', prob: 72, score: 74,
        analysis: '지역 기반 운동 모임과 기록 공유 문화가 결합되며 커뮤니티형 라이프스타일 트렌드로 성장할 가능성이 있습니다.'
    },
    {
        id: 104, name: '업사이클링 패션', cat: 'fashion', prob: 65, score: 68,
        analysis: '친환경 소비와 개성 있는 리폼 콘텐츠가 맞물리며 소규모 브랜드와 중고 플랫폼 중심으로 확산될 수 있습니다.'
    },
    {
        id: 105, name: '초단편 드라마', cat: 'content', prob: 58, score: 62,
        analysis: '숏폼 플랫폼에서 회차형 콘텐츠 소비가 늘면서 짧은 러닝타임의 연속극 포맷이 더 넓어질 가능성이 있습니다.'
    },
    {
        id: 106, name: '슬립테크 루틴', cat: 'technology', prob: 49, score: 54,
        analysis: '수면 측정 기기와 회복 중심 건강 관리 앱이 늘고 있으나 일상 사용 습관으로 자리 잡는지가 관건입니다.'
    },
    {
        id: 107, name: '무알코올 페어링', cat: 'food', prob: 42, score: 47,
        analysis: '저도수/무알코올 음료 관심은 꾸준하지만 외식 메뉴와 함께 소비되는 문화로 확장될지는 더 확인이 필요합니다.'
    },
    {
        id: 108, name: '책맥 모임', cat: 'lifestyle', prob: 34, score: 39,
        analysis: '독서 모임과 가벼운 취향 커뮤니티가 결합된 형태로 니치 수요는 있으나 대중 확산은 아직 제한적입니다.'
    },
    {
        id: 109, name: 'AI 아바타 팬덤', cat: 'content', prob: 27, score: 31,
        analysis: '기술 관심은 높지만 지속적인 팬덤 소비로 이어지려면 캐릭터성과 서사가 더 필요합니다.'
    },
    {
        id: 110, name: '스마트 텃밭', cat: 'lifestyle', prob: 18, score: 24,
        analysis: '홈가드닝과 IoT가 맞닿아 있으나 설치 비용과 관리 난도가 있어 단기 대중화 가능성은 낮습니다.'
    },
]

export const PROB_BADGES = [
    { min: 0, max: 20, bg: '#C97B7B', text: '뱀이 사다리 타고 올라올 확률', sub: '이게 유행한다고요...? 글쎄요' },
    { min: 21, max: 35, bg: '#C49A6C', text: '윷놀이 첫 판에 윷·모 나올 확률', sub: '가능은 하죠, 근데 쉽지 않아요' },
    { min: 36, max: 50, bg: '#B8A84A', text: '동전 던져서 앞면 나올 확률', sub: '반반이에요, 운에 맡겨볼까요?' },
    { min: 51, max: 65, bg: '#8DC98D', text: '편의점 1+1 행사 상품 고를 확률', sub: '슬슬 가능성이 보이네요' },
    { min: 66, max: 79, bg: '#7BA8C9', text: '치킨집 앞 30분 기다리면 자리 날 확률', sub: '꽤 믿을 만해요, 기다려볼 가치 있어요' },
    { min: 80, max: 89, bg: '#A889C9', text: '월요일 아침 지하철 사람 많을 확률', sub: '거의 확실해요, 준비하세요!' },
    { min: 90, max: 100, bg: '#F5E97A', text: '치킨 시키면 고양이가 냄새 맡고 올 확률', sub: 'AI가 강력 추천합니다. 믿으세요' },
]

export const getProbBadge = (prob) =>
    PROB_BADGES.find(b => prob >= b.min && prob <= b.max) || PROB_BADGES[0]
