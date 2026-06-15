export interface ScoreBadgeProps {
  score: number;
}

export function ScoreBadge({ score }: ScoreBadgeProps) {
  const color = 
    score >= 80 ? '#ef4444' :
    score >= 60 ? '#f97316' :
    score >= 40 ? '#eab308' :
    '#6b7280';
  