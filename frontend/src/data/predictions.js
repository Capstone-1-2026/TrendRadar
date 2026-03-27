export const PREDICTIONS = [
    {
        id: 1, name: '두바이초콜릿', cat: 'food', prob: 82, score: 85,
        analysis: 'SNS 확산 속도와 검색량 증가율을 기반으로 높은 유행 가능성을 보입니다. 특히 20대 여성층에서 급격한 관심 증가가 감지되었으며, 글로벌 트렌드 연계성도 높게 나타났습니다.'
    },
    {
        id: 2, name: 'AI피부진단', cat: 'technology', prob: 76, score: 79,
        analysis: 'AI 기술 접목 미용 서비스 수요가 꾸준히 증가하고 있습니다. 뷰티 앱 다운로드 수와 관련 콘텐츠 소비량이 전년 대비 40% 이상 상승했습니다.'
    },
    {
        id: 3, name: '하이볼칵테일', cat: 'food', prob: 68, score: 72,
        analysis: '홈술 문화의 확장과 함께 프리미엄 혼술 키워드가 부상하고 있습니다. 편의점 하이볼 상품 판매량이 전년 동기 대비 62% 증가했습니다.'
    },
    {
        id: 4, name: '미니멀패션', cat: 'fashion', prob: 61, score: 65,
        analysis: '과잉 소비 반작용으로 간결하고 기능적인 스타일 수요가 증가하는 추세입니다.'
    },
    {
        id: 5, name: '버추얼인플루언서', cat: 'content', prob: 54, score: 58,
        analysis: 'AI 생성 가상 인물에 대한 관심이 높아지고 있으나 아직 주류 단계는 아닙니다.'
    },
    {
        id: 6, name: '제로웨이스트쿡', cat: 'lifestyle', prob: 47, score: 51,
        analysis: '친환경 인식 확산에 따른 요리 트렌드로 관심은 있으나 실천율은 아직 낮은 편입니다.'
    },
    {
        id: 7, name: '레트로게임카페', cat: 'content', prob: 39, score: 44,
        analysis: 'Y2K 감성의 연장선으로 향수를 자극하는 오프라인 공간에 대한 수요가 있습니다.'
    },
    {
        id: 8, name: '비건베이킹', cat: 'food', prob: 31, score: 36,
        analysis: '건강·윤리 소비 트렌드와 맞닿아 있으나 국내 소비자 수용도가 아직 낮습니다.'
    },
    {
        id: 9, name: '스페이스코어패션', cat: 'fashion', prob: 22, score: 27,
        analysis: '해외 패션 위크에서 등장하고 있으나 국내 트렌드 반영까지는 시간이 필요합니다.'
    },
    {
        id: 10, name: '달팽이슬라임', cat: 'lifestyle', prob: 14, score: 18,
        analysis: '해외 숏폼에서 간헐적으로 바이럴되고 있으나 국내 확산 사례는 미미합니다.'
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