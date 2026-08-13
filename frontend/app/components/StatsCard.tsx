/**
 * 统计卡片组件
 */

interface StatsCardProps {
  label: string;
  value: string | number;
  icon: string;
  color: 'blue' | 'green' | 'purple' | 'orange';
  subtext?: string;
}

export default function StatsCard({
  label,
  value,
  icon,
  color,
  subtext,
}: StatsCardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200 text-blue-600',
    green: 'bg-green-50 border-green-200 text-green-600',
    purple: 'bg-purple-50 border-purple-200 text-purple-600',
    orange: 'bg-orange-50 border-orange-200 text-orange-600',
  };

  return (
    <div className={`${colorClasses[color]} border rounded-lg p-6`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 text-sm font-medium mb-2">{label}</p>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          {subtext && <p className="text-xs text-gray-500 mt-2">{subtext}</p>}
        </div>
        <div className="text-4xl">{icon}</div>
      </div>
    </div>
  );
}
