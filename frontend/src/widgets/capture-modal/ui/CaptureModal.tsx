// @ts-nocheck
import React, { useState, useEffect } from 'react';
import { X, Sword, Shield, Target, Timer, CheckCircle, XCircle, Loader2, User } from 'lucide-react';
import { api } from '../../../shared/api/base-api';

interface CaptureModalProps {
  territory: any;
  characters: any[];
  onClose: () => void;
  onSuccess: () => void;
}

export const CaptureModal: React.FC<CaptureModalProps> = ({ territory, characters, onClose, onSuccess }) => {
  const [selectedCharId, setSelectedCharId] = useState<number | null>(null);
  const [isStarting, setIsStarting] = useState(false);
  const [activeMission, setActiveMission] = useState<any>(null);
  const [timeLeft, setTimeLeft] = useState(0);
  const [result, setResult] = useState<'success' | 'fail' | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Timer countdown
  useEffect(() => {
    if (timeLeft <= 0 || result) return;
    const timer = setTimeout(() => setTimeLeft(prev => prev - 1), 1000);
    return () => clearTimeout(timer);
  }, [timeLeft, result]);

  const handleStartCapture = async () => {
    if (!selectedCharId) return;
    setIsStarting(true);
    setError(null);

    try {
      const res = await api.post(`/territories/${territory.id}/capture/`, {
        character_ids: [selectedCharId],
      });

      if (res.success && res.mission_id) {
        setActiveMission(res);
        setTimeLeft(res.duration || 30);
      } else {
        setError(res.message || 'Не удалось начать миссию');
      }
    } catch (e: any) {
      setError(e.message || 'Ошибка сети');
    } finally {
      setIsStarting(false);
    }
  };

  const handleComplete = async () => {
    if (!activeMission?.user_mission_id) return;

    try {
      const res = await api.post(`/user_missions/${activeMission.user_mission_id}/complete/`);

      if (res.success) {
        setResult('success');
        setTimeout(() => onSuccess(), 2000);
      } else {
        setResult('fail');
      }
    } catch (e: any) {
      setError(e.message || 'Ошибка завершения миссии');
    }
  };

  // Auto-complete when timer ends
  useEffect(() => {
    if (timeLeft <= 0 && activeMission && !result) {
      handleComplete();
    }
  }, [timeLeft, activeMission, result]);

  // Phase 1: Character selection
  if (!activeMission) {
    return (
      <div className="fixed inset-0 z-50 bg-black/80 flex items-end sm:items-center justify-center p-0 sm:p-4">
        <div className="bg-gray-900 rounded-t-2xl sm:rounded-2xl border border-gray-800 w-full sm:max-w-md max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-800">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Target className="w-5 h-5 text-green-400" />
              Захват территории
            </h2>
            <button onClick={onClose} className="text-gray-400 hover:text-white">
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Territory info */}
          <div className="p-4 border-b border-gray-800">
            <div className="font-bold text-white mb-1">{territory.name}</div>
            <div className="text-sm text-gray-400 flex flex-wrap gap-3">
              <span className="flex items-center gap-1">
                <Sword className="w-4 h-4 text-red-400" /> 💪 {territory.power_required}
              </span>
              <span className="flex items-center gap-1">
                <Shield className="w-4 h-4 text-blue-400" /> 🧠 {territory.intellect_required}
              </span>
              <span className="flex items-center gap-1">
                <Target className="w-4 h-4 text-green-400" /> ⚡ {territory.agility_required}
              </span>
            </div>
          </div>

          {/* Character selection */}
          <div className="p-4">
            <h3 className="text-sm font-semibold text-gray-300 mb-3">Выбери бойца:</h3>
            {characters.length === 0 ? (
              <p className="text-gray-500 text-sm">У тебя нет бойцов</p>
            ) : (
              <div className="space-y-2">
                {characters.map((char: any) => (
                  <button
                    key={char.id}
                    className={`w-full p-3 rounded-lg border transition-all text-left ${
                      selectedCharId === char.id
                        ? 'border-green-500 bg-green-900/30'
                        : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                    }`}
                    onClick={() => setSelectedCharId(char.id)}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        selectedCharId === char.id ? 'bg-green-600' : 'bg-gray-700'
                      }`}>
                        <User className="w-5 h-5 text-white" />
                      </div>
                      <div className="flex-1">
                        <div className="font-bold text-white text-sm">{char.name}</div>
                        <div className="text-xs text-gray-400 capitalize">{char.role}</div>
                      </div>
                      <div className="flex gap-2 text-xs">
                        <span className="text-red-400">💪{char.power}</span>
                        <span className="text-blue-400">🧠{char.intellect}</span>
                        <span className="text-green-400">⚡{char.agility}</span>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}

            {error && (
              <div className="mt-3 p-2 bg-red-900/50 border border-red-800 rounded text-sm text-red-300">
                {error}
              </div>
            )}

            {/* Start button */}
            <button
              className="w-full mt-4 py-3 bg-green-600 hover:bg-green-500 disabled:bg-gray-700 disabled:text-gray-500 text-white font-bold rounded-lg transition-all flex items-center justify-center gap-2"
              disabled={!selectedCharId || isStarting}
              onClick={handleStartCapture}
            >
              {isStarting ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Начинаю...
                </>
              ) : (
                <>
                  <Sword className="w-5 h-5" />
                  Начать захват
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Phase 2: Mission in progress
  if (!result) {
    const progress = activeMission.duration
      ? ((activeMission.duration - timeLeft) / activeMission.duration) * 100
      : 0;

    return (
      <div className="fixed inset-0 z-50 bg-black/80 flex items-end sm:items-center justify-center p-0 sm:p-4">
        <div className="bg-gray-900 rounded-t-2xl sm:rounded-2xl border border-gray-800 w-full sm:max-w-md">
          <div className="p-6 text-center">
            <div className="relative w-24 h-24 mx-auto mb-4">
              <svg className="w-24 h-24 -rotate-90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" stroke="#374151" strokeWidth="8" fill="none" />
                <circle
                  cx="50"
                  cy="50"
                  r="45"
                  stroke="#22c55e"
                  strokeWidth="8"
                  fill="none"
                  strokeDasharray={`${progress * 2.83} 283`}
                  className="transition-all duration-1000"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <Timer className="w-8 h-8 text-green-400" />
              </div>
            </div>
            <h2 className="text-xl font-bold text-white mb-2">Захват идёт...</h2>
            <div className="text-3xl font-bold text-green-400 mb-2">{timeLeft}с</div>
            <p className="text-sm text-gray-400">
              Боец выполняет миссию захвата
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Phase 3: Result
  return (
    <div className="fixed inset-0 z-50 bg-black/80 flex items-end sm:items-center justify-center p-0 sm:p-4">
      <div className="bg-gray-900 rounded-t-2xl sm:rounded-2xl border border-gray-800 w-full sm:max-w-md">
        <div className="p-6 text-center">
          {result === 'success' ? (
            <>
              <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-4" />
              <h2 className="text-xl font-bold text-white mb-2">Территория захвачена!</h2>
              <div className="space-y-1 text-sm">
                <p className="text-green-300">+{territory.reward_money} 💰</p>
                <p className="text-green-300">+{territory.reward_influence} 🌐</p>
                <p className="text-gray-400">Доход: +{territory.passive_income_money}💰/тик</p>
              </div>
            </>
          ) : (
            <>
              <XCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
              <h2 className="text-xl font-bold text-white mb-2">Миссия провалена</h2>
              <p className="text-sm text-gray-400">Попробуй снова когда будешь сильнее</p>
            </>
          )}
          <button
            className="w-full mt-6 py-3 bg-gray-700 hover:bg-gray-600 text-white font-bold rounded-lg"
            onClick={onClose}
          >
            Закрыть
          </button>
        </div>
      </div>
    </div>
  );
};
