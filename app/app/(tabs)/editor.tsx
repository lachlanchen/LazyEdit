import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import {
  ActivityIndicator,
  FlatList,
  Image,
  Modal,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TextInput,
  type ViewToken,
  View,
} from 'react-native';

import { useI18n } from '@/components/I18nProvider';
import { subscribeStudioRefresh, triggerStudioRefresh } from '@/lib/studioRefresh';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8787';
const PAGE_SIZE = 8;
const PROCESS_READY_TIMEOUT_MS = 90 * 60 * 1000;
const AVAILABLE_TRANSLATION_LANGUAGES = ['ja', 'en', 'zh-Hant', 'fr'];
const DEFAULT_TRANSLATION_LANGUAGES = ['ja', 'en', 'zh-Hant'];
const DEFAULT_SUBTITLE_LIFT_RATIO = 0.1;
const MIN_SUBTITLE_LIFT_RATIO = 0;
const MAX_SUBTITLE_LIFT_RATIO = 0.4;
const DEFAULT_SUBTITLE_ROWS = 4;
const MIN_SUBTITLE_ROWS = 1;
const MAX_SUBTITLE_ROWS = 10;
const DEFAULT_SUBTITLE_FONT_SCALE = 1;
const MIN_SUBTITLE_FONT_SCALE = 0.6;
const MAX_SUBTITLE_FONT_SCALE = 2.5;
const DEFAULT_SUBTITLE_FONT_COLOR = '#FFFFFF';
const DEFAULT_SUBTITLE_OUTLINE_COLOR = '#000000';
const DEFAULT_PORTRAIT_FOREGROUND_Y = 240;
const MIN_PORTRAIT_FOREGROUND_Y = 0;
const MAX_PORTRAIT_FOREGROUND_Y = 1920;
const DEFAULT_PORTRAIT_BOTTOM_SPACE_RATIO = 0.4;
const MIN_PORTRAIT_BOTTOM_SPACE_RATIO = 0;
const MAX_PORTRAIT_BOTTOM_SPACE_RATIO = 0.8;
const PORTRAIT_OUTPUT_WIDTH = 1080;
const PORTRAIT_OUTPUT_HEIGHT = 1920;
const DEFAULT_CORRECTION_PROMPT =
  'Fix recognition errors while preserving every timestamp exactly and keeping the same number of subtitle lines.';
const LANGUAGE_LABELS: Record<string, string> = {
  ja: 'Japanese',
  en: 'English',
  'zh-Hant': 'Chinese',
  fr: 'French',
};
const LANGUAGE_SHORT_LABELS: Record<string, string> = {
  ja: 'JP',
  en: 'EN',
  'zh-Hant': 'ZH',
  fr: 'FR',
};

type Video = {
  id: number;
  title: string | null;
  file_path: string;
  media_url?: string | null;
  preview_media_url?: string | null;
  preview_image_url?: string | null;
  needs_preview_proxy?: boolean;
  has_preview_proxy?: boolean;
  has_preview_image?: boolean;
  created_at?: string;
};

type PublishJob = {
  id?: string | number;
  video_id?: number | null;
  filename?: string;
  title?: string | null;
  status?: string;
  detail?: string;
  created_at?: string;
  updated_at?: string;
  platforms?: string[];
  error?: string;
  zip_url?: string | null;
  source?: string;
};

type ProcessStep = {
  status?: string;
  detail?: string;
  updated_at?: string;
  progress?: number;
};

type LogoSettings = {
  logoPath?: string | null;
  logoUrl?: string | null;
  heightRatio?: number;
  position?: string;
  bgOpacity?: number;
  bgShape?: string;
  enabled?: boolean;
};

type PublicationSession = {
  id: number;
  title?: string | null;
  mode?: string;
  status?: string;
  burn?: {
    status?: string | null;
    output_url?: string | null;
    progress?: number | null;
    error?: string | null;
    created_at?: string | null;
  } | null;
  burn_output_url?: string | null;
  burn_status?: string | null;
  created_at?: string;
  updated_at?: string;
};

type SubtitleCorrectionPayload = {
  original?: { text?: string; preview_text?: string } | null;
  polished?: { text?: string; preview_text?: string } | null;
  publication_session_id?: number | null;
};

type SubtitleSourceVariant = 'polished' | 'original';
type PortraitBlurMode = 'lalachan' | 'center' | 'custom';

type VideoDimensions = {
  width: number;
  height: number;
};

type PortraitLayoutMetrics = {
  outputWidth: number;
  outputHeight: number;
  sourceWidth: number;
  sourceHeight: number;
  foregroundWidth: number;
  foregroundHeight: number;
  top: number;
  bottom: number;
  centerShift: number;
  centerShiftRatio: number;
  narrowed: boolean;
};

const PLATFORMS = [
  { key: 'douyin', label: 'Douyin' },
  { key: 'xiaohongshu', label: 'Xiaohongshu' },
  { key: 'shipinhao', label: 'Shipinhao' },
  { key: 'bilibili', label: 'Bilibili' },
  { key: 'youtube', label: 'YouTube' },
  { key: 'instagram', label: 'Instagram' },
];
const MUSIC_PLATFORMS = [
  { key: 'shipinhao_music', label: 'Shipinhao Music' },
  { key: 'youtube_music', label: 'YouTube Music' },
];
const withCacheBust = (url: string) => `${url}${url.includes('?') ? '&' : '?'}t=${Date.now()}`;
const normalizeSubtitleLiftRatio = (value: unknown, fallback = DEFAULT_SUBTITLE_LIFT_RATIO) => {
  const parsed = typeof value === 'number' ? value : Number(String(value ?? '').trim());
  if (!Number.isFinite(parsed)) return fallback;
  const clamped = Math.min(MAX_SUBTITLE_LIFT_RATIO, Math.max(MIN_SUBTITLE_LIFT_RATIO, parsed));
  return Math.round(clamped * 1000) / 1000;
};
const formatSubtitleLiftRatio = (value: number) => {
  const normalized = normalizeSubtitleLiftRatio(value);
  return normalized.toFixed(3).replace(/0+$/, '').replace(/\.$/, '');
};
const normalizeSubtitleRows = (value: unknown, fallback = DEFAULT_SUBTITLE_ROWS) => {
  const parsed = typeof value === 'number' ? value : Number(String(value ?? '').trim());
  if (!Number.isFinite(parsed)) return fallback;
  return Math.min(MAX_SUBTITLE_ROWS, Math.max(MIN_SUBTITLE_ROWS, Math.round(parsed)));
};
const normalizeSubtitleFontScale = (value: unknown, fallback = DEFAULT_SUBTITLE_FONT_SCALE) => {
  const parsed = typeof value === 'number' ? value : Number(String(value ?? '').trim());
  if (!Number.isFinite(parsed)) return fallback;
  const clamped = Math.min(MAX_SUBTITLE_FONT_SCALE, Math.max(MIN_SUBTITLE_FONT_SCALE, parsed));
  return Math.round(clamped * 100) / 100;
};
const formatSubtitleFontScale = (value: number) => {
  const normalized = normalizeSubtitleFontScale(value);
  return normalized.toFixed(2).replace(/0+$/, '').replace(/\.$/, '');
};
const normalizeHexColor = (value: unknown, fallback: string) => {
  const text = String(value ?? '').trim();
  if (!/^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/.test(text)) return fallback;
  if (text.length === 4) {
    return `#${text.slice(1).split('').map((char) => char + char).join('')}`.toUpperCase();
  }
  return text.toUpperCase();
};
const normalizePortraitMode = (value: unknown): PortraitBlurMode => {
  const text = String(value ?? '').trim().toLowerCase();
  if (text === 'center' || text === 'custom') return text;
  return 'lalachan';
};
const normalizePortraitForegroundY = (value: unknown, fallback = DEFAULT_PORTRAIT_FOREGROUND_Y) => {
  const parsed = typeof value === 'number' ? value : Number(String(value ?? '').trim());
  if (!Number.isFinite(parsed)) return fallback;
  return Math.min(MAX_PORTRAIT_FOREGROUND_Y, Math.max(MIN_PORTRAIT_FOREGROUND_Y, Math.round(parsed)));
};
const normalizePortraitBottomSpaceRatio = (value: unknown, fallback = DEFAULT_PORTRAIT_BOTTOM_SPACE_RATIO) => {
  const parsed = typeof value === 'number' ? value : Number(String(value ?? '').trim());
  if (!Number.isFinite(parsed)) return fallback;
  const clamped = Math.min(MAX_PORTRAIT_BOTTOM_SPACE_RATIO, Math.max(MIN_PORTRAIT_BOTTOM_SPACE_RATIO, parsed));
  return Math.round(clamped * 1000) / 1000;
};
const formatPortraitBottomSpaceRatio = (value: number) => {
  const normalized = normalizePortraitBottomSpaceRatio(value);
  return normalized.toFixed(3).replace(/0+$/, '').replace(/\.$/, '');
};
const evenAtLeast = (value: number, minimum = 2) => {
  const rounded = Math.max(minimum, Math.floor(value));
  const even = rounded % 2 ? rounded - 1 : rounded;
  return Math.max(minimum, even);
};
const scaledForegroundHeight = (sourceWidth: number, sourceHeight: number, foregroundWidth: number) => {
  const scaled = Math.round(sourceHeight * (foregroundWidth / Math.max(sourceWidth, 1)));
  return Math.max(2, scaled % 2 ? scaled + 1 : scaled);
};
const calculatePortraitLayoutMetrics = (
  source: VideoDimensions | null,
  mode: PortraitBlurMode,
  bottomSpaceRatio: number,
  foregroundY: number,
): PortraitLayoutMetrics | null => {
  if (!source || source.width <= 0 || source.height <= 0) return null;
  const outputWidth = PORTRAIT_OUTPUT_WIDTH;
  const outputHeight = PORTRAIT_OUTPUT_HEIGHT;
  const requestedWidth = outputWidth;
  const desiredBottom = mode === 'lalachan'
    ? Math.min(Math.max(Math.round(outputHeight * bottomSpaceRatio), 0), outputHeight - 2)
    : 0;
  const maxForegroundHeight = mode === 'lalachan'
    ? Math.max(2, outputHeight - desiredBottom)
    : outputHeight;
  let foregroundWidth = evenAtLeast(requestedWidth);
  let foregroundHeight = scaledForegroundHeight(source.width, source.height, foregroundWidth);
  if (foregroundHeight > maxForegroundHeight) {
    foregroundWidth = evenAtLeast(Math.min(foregroundWidth, maxForegroundHeight * (source.width / Math.max(source.height, 1))));
    foregroundHeight = scaledForegroundHeight(source.width, source.height, foregroundWidth);
    while (foregroundWidth > 2 && foregroundHeight > maxForegroundHeight) {
      foregroundWidth -= 2;
      foregroundHeight = scaledForegroundHeight(source.width, source.height, foregroundWidth);
    }
  }
  const maxY = Math.max(0, outputHeight - foregroundHeight);
  const centerY = Math.floor(maxY / 2);
  let top = centerY;
  if (mode === 'lalachan') {
    top = Math.min(Math.max(outputHeight - foregroundHeight - desiredBottom, 0), maxY);
  } else if (mode === 'custom') {
    top = Math.min(Math.max(foregroundY, 0), maxY);
  }
  const bottom = Math.max(0, outputHeight - top - foregroundHeight);
  const centerShift = centerY - top;
  return {
    outputWidth,
    outputHeight,
    sourceWidth: source.width,
    sourceHeight: source.height,
    foregroundWidth,
    foregroundHeight,
    top,
    bottom,
    centerShift,
    centerShiftRatio: centerY ? centerShift / centerY : 0,
    narrowed: foregroundWidth < requestedWidth,
  };
};
const formatMetricPercent = (value: number) => `${Math.round(value * 100)}%`;

export default function EditorScreen() {
  const defaultPublishSelection = useMemo(
    () => ({
      douyin: false,
      xiaohongshu: true,
      shipinhao: true,
      bilibili: false,
      youtube: true,
      instagram: true,
    }),
    [],
  );
  const [selected, setSelected] = useState<Record<string, boolean>>(defaultPublishSelection);
  const [publishMode, setPublishMode] = useState<'video' | 'music'>('video');
  const [musicSelected, setMusicSelected] = useState<Record<string, boolean>>({
    shipinhao_music: true,
    youtube_music: true,
  });
  const [musicAudioPath, setMusicAudioPath] = useState('');
  const [musicTitle, setMusicTitle] = useState('');
  const [musicAuthor, setMusicAuthor] = useState('Musia 慕莎');
  const [musicArtist, setMusicArtist] = useState('Musia 慕莎');
  const [musicLanguage, setMusicLanguage] = useState('中文');
  const [musicGenre, setMusicGenre] = useState('流行');
  const [musicLyricsText, setMusicLyricsText] = useState('');
  const [musicLyricsPath, setMusicLyricsPath] = useState('');
  const [musicLyricsJsonPath, setMusicLyricsJsonPath] = useState('');
  const [musicStory, setMusicStory] = useState('');
  const [musicDescription, setMusicDescription] = useState('');
  const [musicCoverPaths, setMusicCoverPaths] = useState('');
  const [musicCoverVideoPath, setMusicCoverVideoPath] = useState('');
  const [musicCoverCount, setMusicCoverCount] = useState('9');
  const [musicCoverModel, setMusicCoverModel] = useState('aginti+codex');
  const [musicAgintiCoverCount, setMusicAgintiCoverCount] = useState('5');
  const [musicCodexCoverCount, setMusicCodexCoverCount] = useState('4');
  const [musicProofPaths, setMusicProofPaths] = useState('');
  const [musicWebsiteScreenshot, setMusicWebsiteScreenshot] = useState('');
  const [musicWebappScreenshot, setMusicWebappScreenshot] = useState('');
  const [musicSourceUrl, setMusicSourceUrl] = useState('');
  const [musicOutputSlug, setMusicOutputSlug] = useState('');
  const [musicPackaging, setMusicPackaging] = useState(false);
  const [musicStatus, setMusicStatus] = useState('');
  const [musicTone, setMusicTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [musicZipUrl, setMusicZipUrl] = useState<string | null>(null);
  const [videos, setVideos] = useState<Video[]>([]);
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);
  const [listHeight, setListHeight] = useState(0);
  const [listContentHeight, setListContentHeight] = useState(0);
  const [loadingVideos, setLoadingVideos] = useState(false);
  const [selectedVideoId, setSelectedVideoId] = useState<number | null>(null);
  const [confirmDeleteVideo, setConfirmDeleteVideo] = useState<Video | null>(null);
  const [deleteVideoPending, setDeleteVideoPending] = useState(false);
  const [deleteVideoError, setDeleteVideoError] = useState('');
  const [coverUrl, setCoverUrl] = useState<string | null>(null);
  const [coverStatus, setCoverStatus] = useState('');
  const [coverTone, setCoverTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [coverLoading, setCoverLoading] = useState(false);
  const [processRunning, setProcessRunning] = useState(false);
  const [processStatus, setProcessStatus] = useState('');
  const [processTone, setProcessTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [processSteps, setProcessSteps] = useState<Record<string, ProcessStep> | null>(null);
  const [processUpdatedAt, setProcessUpdatedAt] = useState<string | null>(null);
  const [processReadyForCover, setProcessReadyForCover] = useState(false);
  const [processReadyForPublish, setProcessReadyForPublish] = useState(false);
  const [processStatusLoading, setProcessStatusLoading] = useState(false);
  const [processStatusError, setProcessStatusError] = useState('');
  const [publishing, setPublishing] = useState(false);
  const [publishStatus, setPublishStatus] = useState('');
  const [publishTone, setPublishTone] = useState<'neutral' | 'good' | 'bad'>('neutral');
  const [publishZipUrl, setPublishZipUrl] = useState<string | null>(null);
  const [publishQueue, setPublishQueue] = useState<PublishJob[]>([]);
  const [queueLoading, setQueueLoading] = useState(false);
  const [queueError, setQueueError] = useState('');
  const [queueExpanded, setQueueExpanded] = useState(false);
  const [publishSettingsLoaded, setPublishSettingsLoaded] = useState(false);
  const [publishOptionsLoaded, setPublishOptionsLoaded] = useState(false);
  const [burnSubtitles, setBurnSubtitles] = useState(true);
  const [usePolishedSubtitles, setUsePolishedSubtitles] = useState(true);
  const [subtitleSourceMenuOpen, setSubtitleSourceMenuOpen] = useState(false);
  const [publishAsNewSession, setPublishAsNewSession] = useState(false);
  const [publicationSessionId, setPublicationSessionId] = useState<number | null>(null);
  const [publicationSessions, setPublicationSessions] = useState<PublicationSession[]>([]);
  const [sessionLoading, setSessionLoading] = useState(false);
  const [runSelectionTouched, setRunSelectionTouched] = useState(false);
  const [processRunMenuOpen, setProcessRunMenuOpen] = useState(false);
  const [publishRunMenuOpen, setPublishRunMenuOpen] = useState(false);
  const [previewSourceKey, setPreviewSourceKey] = useState('original');
  const [previewSourceMenuOpen, setPreviewSourceMenuOpen] = useState(false);
  const [baseBurnPreviewUrl, setBaseBurnPreviewUrl] = useState<string | null>(null);
  const [baseBurnPreviewStatus, setBaseBurnPreviewStatus] = useState<string | null>(null);
  const [translationLanguages, setTranslationLanguages] = useState<string[]>(DEFAULT_TRANSLATION_LANGUAGES);
  const [subtitleLiftRatio, setSubtitleLiftRatio] = useState(DEFAULT_SUBTITLE_LIFT_RATIO);
  const [subtitleLiftInput, setSubtitleLiftInput] = useState(formatSubtitleLiftRatio(DEFAULT_SUBTITLE_LIFT_RATIO));
  const [subtitleRows, setSubtitleRows] = useState(DEFAULT_SUBTITLE_ROWS);
  const [subtitleRowsInput, setSubtitleRowsInput] = useState(String(DEFAULT_SUBTITLE_ROWS));
  const [subtitleFontScale, setSubtitleFontScale] = useState(DEFAULT_SUBTITLE_FONT_SCALE);
  const [subtitleFontScaleInput, setSubtitleFontScaleInput] = useState(formatSubtitleFontScale(DEFAULT_SUBTITLE_FONT_SCALE));
  const [subtitleFontBold, setSubtitleFontBold] = useState(true);
  const [subtitleFontColor, setSubtitleFontColor] = useState(DEFAULT_SUBTITLE_FONT_COLOR);
  const [subtitleOutlineBold, setSubtitleOutlineBold] = useState(true);
  const [subtitleOutlineColor, setSubtitleOutlineColor] = useState(DEFAULT_SUBTITLE_OUTLINE_COLOR);
  const [portraitBlurFill, setPortraitBlurFill] = useState(false);
  const [portraitBlurMode, setPortraitBlurMode] = useState<PortraitBlurMode>('lalachan');
  const [portraitForegroundY, setPortraitForegroundY] = useState(DEFAULT_PORTRAIT_FOREGROUND_Y);
  const [portraitForegroundYInput, setPortraitForegroundYInput] = useState(String(DEFAULT_PORTRAIT_FOREGROUND_Y));
  const [portraitBottomSpaceRatio, setPortraitBottomSpaceRatio] = useState(DEFAULT_PORTRAIT_BOTTOM_SPACE_RATIO);
  const [portraitBottomSpaceInput, setPortraitBottomSpaceInput] = useState(
    formatPortraitBottomSpaceRatio(DEFAULT_PORTRAIT_BOTTOM_SPACE_RATIO),
  );
  const [sourceVideoDimensions, setSourceVideoDimensions] = useState<VideoDimensions | null>(null);
  const [portraitLayoutModalOpen, setPortraitLayoutModalOpen] = useState(false);
  const [correctionOpen, setCorrectionOpen] = useState(false);
  const [correctionLoading, setCorrectionLoading] = useState(false);
  const [correctionSaving, setCorrectionSaving] = useState(false);
  const [correctionStatus, setCorrectionStatus] = useState('');
  const [correctionPrompt, setCorrectionPrompt] = useState(DEFAULT_CORRECTION_PROMPT);
  const [correctionSourceVariant, setCorrectionSourceVariant] = useState<SubtitleSourceVariant>('polished');
  const [useCorrectionPromptForMetadata, setUseCorrectionPromptForMetadata] = useState(true);
  const [autoCorrectSubtitles, setAutoCorrectSubtitles] = useState(false);
  const [autoCorrectPrompt, setAutoCorrectPrompt] = useState('');
  const [autoCorrectDraftPrompt, setAutoCorrectDraftPrompt] = useState('');
  const [autoCorrectPromptOpen, setAutoCorrectPromptOpen] = useState(false);
  const [autoCorrectPromptError, setAutoCorrectPromptError] = useState('');
  const [originalSubtitleText, setOriginalSubtitleText] = useState('');
  const [polishedSubtitleText, setPolishedSubtitleText] = useState('');
  const previewProxyPendingIdsRef = useRef<number[]>([]);
  const previewProxyAttemptedIdsRef = useRef<Set<number>>(new Set());
  const previewProxyRunningRef = useRef(false);
  const videosRef = useRef<Video[]>([]);
  const queueVisiblePreviewBackfillRef = useRef<(items: Video[]) => void>(() => {});
  const viewabilityConfigRef = useRef({ itemVisiblePercentThreshold: 60, minimumViewTime: 120 });
  const coverRequestIdRef = useRef(0);
  const { t } = useI18n();

  const resolveMediaSrc = useCallback((value?: string | null) => {
    if (!value) return null;
    if (value.startsWith('http://') || value.startsWith('https://')) return value;
    return `${API_URL}${value}`;
  }, []);

  const processStepDefinitions = useMemo(
    () => [
      { key: 'transcribe', label: t('publish_step_transcribe') },
      { key: 'polish', label: t('publish_step_polish') },
      { key: 'translate', label: t('publish_step_translate') },
      { key: 'burn', label: t('publish_step_burn') },
      { key: 'keyframes', label: t('publish_step_keyframes') },
      { key: 'caption', label: t('publish_step_caption') },
      { key: 'metadata_zh', label: t('publish_step_metadata_zh') },
      { key: 'metadata_en', label: t('publish_step_metadata_en') },
      { key: 'cover', label: t('publish_step_cover') },
    ],
    [t],
  );

  const processStepLabelMap = useMemo(
    () => Object.fromEntries(processStepDefinitions.map(({ key, label }) => [key, label])),
    [processStepDefinitions],
  );

  const processBusy = useMemo(() => {
    if (!processSteps) return processRunning;
    return processRunning || Object.values(processSteps).some((step) => {
      const status = String(step?.status || '').toLowerCase();
      return status === 'working' || status === 'processing' || status === 'queued';
    });
  }, [processRunning, processSteps]);

  const activeProcessLabel = useMemo(() => {
    if (!processSteps) return null;
    const active = processStepDefinitions.find(({ key }) => {
      const status = String(processSteps[key]?.status || '').toLowerCase();
      return status === 'working' || status === 'processing' || status === 'queued';
    });
    return active?.label || null;
  }, [processSteps, processStepDefinitions]);

  const processButtonLabel = useMemo(() => {
    if (processRunning) return t('publish_process_starting');
    if (processBusy) {
      return activeProcessLabel
        ? t('publish_process_running_step', { value: activeProcessLabel })
        : t('publish_process_running');
    }
    return t('publish_process_button');
  }, [processRunning, processBusy, activeProcessLabel, t]);

  const summarizeProcessState = useCallback(
    (steps?: Record<string, ProcessStep> | null) => {
      for (const { key } of processStepDefinitions) {
        const step = steps?.[key];
        const status = String(step?.status || '').toLowerCase();
        if (status === 'error' || status === 'failed') {
          return {
            activeLabel: null as string | null,
            errorDetail: step?.detail || processStepLabelMap[key] || key,
          };
        }
      }
      for (const { key } of processStepDefinitions) {
        const step = steps?.[key];
        const status = String(step?.status || '').toLowerCase();
        if (status === 'working' || status === 'processing' || status === 'queued') {
          return {
            activeLabel: processStepLabelMap[key] || key,
            errorDetail: null as string | null,
          };
        }
      }
      return { activeLabel: null as string | null, errorDetail: null as string | null };
    },
    [processStepDefinitions, processStepLabelMap],
  );

  const processStatusLabel = useCallback(
    (status?: string) => {
      const key = String(status || '').toLowerCase();
      if (key === 'done') return t('publish_step_status_done');
      if (key === 'working') return t('publish_step_status_working');
      if (key === 'error') return t('publish_step_status_error');
      if (key === 'skipped') return t('publish_step_status_skipped');
      if (key === 'idle') return t('publish_step_status_idle');
      return status || t('publish_step_status_idle');
    },
    [t],
  );

  const selectedList = useMemo(
    () => PLATFORMS.filter((platform) => selected[platform.key]).map((platform) => platform.label),
    [selected],
  );
  const selectedMusicList = useMemo(
    () => MUSIC_PLATFORMS.filter((platform) => musicSelected[platform.key]).map((platform) => platform.label),
    [musicSelected],
  );
  const selectedVideo = useMemo(
    () => videos.find((video) => video.id === selectedVideoId) || null,
    [videos, selectedVideoId],
  );
  const previewVideoUrl = useMemo(() => {
    if (!selectedVideo) return null;
    const raw = selectedVideo.preview_media_url || selectedVideo.media_url;
    if (!raw) return null;
    return raw.startsWith('http') ? raw : `${API_URL}${raw}`;
  }, [selectedVideo]);
  const previewPosterUrl = useMemo(() => {
    if (!selectedVideo?.preview_image_url) return null;
    const raw = selectedVideo.preview_image_url;
    return raw.startsWith('http') ? raw : `${API_URL}${raw}`;
  }, [selectedVideo]);
  const publicationSessionOrdinalMap = useMemo(() => {
    const sorted = [...publicationSessions].sort((a, b) => {
      const aTime = Date.parse(a.created_at || '') || 0;
      const bTime = Date.parse(b.created_at || '') || 0;
      if (aTime !== bTime) return aTime - bTime;
      return a.id - b.id;
    });
    return new Map(sorted.map((session, index) => [session.id, index + 1]));
  }, [publicationSessions]);
  const publicationSessionLabel = useCallback(
    (session: PublicationSession) =>
      t('publish_run_existing', { value: publicationSessionOrdinalMap.get(session.id) || session.id }),
    [publicationSessionOrdinalMap, t],
  );
  const previewSourceOptions = useMemo(() => {
    const options: Array<{
      key: string;
      label: string;
      hint: string;
      url: string | null;
      poster?: string | null;
    }> = [
      {
        key: 'original',
        label: t('publish_preview_original'),
        hint: t('publish_preview_original_hint'),
        url: previewVideoUrl,
        poster: previewPosterUrl,
      },
    ];
    options.push({
      key: 'base-burn',
      label: t('publish_preview_current_burn'),
      hint:
        baseBurnPreviewStatus === 'completed'
          ? t('publish_preview_burn_ready')
          : t('publish_preview_burn_missing'),
      url: baseBurnPreviewUrl,
      poster: null,
    });
    publicationSessions.forEach((session) => {
      const title = session.title || `Session ${session.id}`;
      const outputUrl = session.burn_output_url || session.burn?.output_url || null;
      const status = session.burn_status || session.burn?.status || '';
      options.push({
        key: `session:${session.id}`,
        label: `${publicationSessionLabel(session)} · ${title}`,
        hint:
          status === 'completed'
            ? t('publish_preview_burn_ready')
            : status
              ? t('publish_preview_burn_status', { value: status })
              : t('publish_preview_burn_missing'),
        url: outputUrl ? resolveMediaSrc(outputUrl) : null,
        poster: null,
      });
    });
    return options;
  }, [
    baseBurnPreviewStatus,
    baseBurnPreviewUrl,
    previewPosterUrl,
    previewVideoUrl,
    publicationSessions,
    publicationSessionLabel,
    resolveMediaSrc,
    t,
  ]);
  const selectedPreviewSource = useMemo(
    () =>
      previewSourceOptions.find((option) => option.key === previewSourceKey) ||
      previewSourceOptions[0],
    [previewSourceKey, previewSourceOptions],
  );
  const selectedPreviewUrl = selectedPreviewSource?.url || null;
  const selectedPreviewPosterUrl = selectedPreviewSource?.poster || previewPosterUrl;
  const portraitLayoutMetrics = useMemo(
    () =>
      calculatePortraitLayoutMetrics(
        sourceVideoDimensions,
        portraitBlurMode,
        portraitBottomSpaceRatio,
        portraitForegroundY,
      ),
    [portraitBlurMode, portraitBottomSpaceRatio, portraitForegroundY, sourceVideoDimensions],
  );
  const visibleVideos = useMemo(() => videos.slice(0, visibleCount), [videos, visibleCount]);
  const hasMoreVideos = visibleCount < videos.length;
  const activeQueueCount = useMemo(
    () => publishQueue.filter((job) => {
      const status = String(job.status || '').toLowerCase();
      return status === 'queued' || status === 'running';
    }).length,
    [publishQueue],
  );

  const splitPathLines = useCallback((value: string) =>
    value
      .split(/\r?\n/)
      .map((item) => item.trim())
      .filter(Boolean), []);
  const selectedPublishJob = useMemo(
    () => publishQueue.find((job) => job.video_id === selectedVideoId) || null,
    [publishQueue, selectedVideoId],
  );
  const selectedRunKey = publishAsNewSession
    ? 'new'
    : publicationSessionId
      ? `session:${publicationSessionId}`
      : 'base';
  const publicationRunOptions = useMemo(() => {
    const options: Array<{
      key: string;
      label: string;
      hint: string;
      session?: PublicationSession;
    }> = [
      {
        key: 'base',
        label: t('publish_run_current'),
        hint: t('publish_run_current_hint'),
      },
    ];
    publicationSessions.forEach((session) => {
      const title = session.title || `Session ${session.id}`;
      const time = formatTimestamp(session.updated_at || session.created_at || '');
      options.push({
        key: `session:${session.id}`,
        label: `${publicationSessionLabel(session)} · ${title}`,
        hint: time || t('publish_run_existing_hint'),
        session,
      });
    });
    options.push({
      key: 'new',
      label: t('publish_run_new'),
      hint: t('publish_run_new_hint'),
    });
    return options;
  }, [publicationSessionLabel, publicationSessions, t]);
  const selectedRunOption = useMemo(
    () =>
      publicationRunOptions.find((option) => option.key === selectedRunKey) ||
      publicationRunOptions[0],
    [publicationRunOptions, selectedRunKey],
  );
  const selectedCoverSessionId = publishAsNewSession ? null : publicationSessionId;
  const subtitleSourceOptions = useMemo(
    () => [
      {
        key: 'polished' as SubtitleSourceVariant,
        label: t('publish_subtitle_source_latest'),
        hint: t('publish_subtitle_source_latest_hint'),
      },
      {
        key: 'original' as SubtitleSourceVariant,
        label: t('publish_subtitle_source_original'),
        hint: t('publish_subtitle_source_original_hint'),
      },
    ],
    [t],
  );
  const selectedSubtitleSource = useMemo(
    () =>
      subtitleSourceOptions.find((option) => option.key === (usePolishedSubtitles ? 'polished' : 'original')) ||
      subtitleSourceOptions[0],
    [subtitleSourceOptions, usePolishedSubtitles],
  );
  const autoCorrectActive = autoCorrectSubtitles && autoCorrectPrompt.trim().length > 0;
  const metadataCorrectionPrompt = useMemo(() => {
    if (!useCorrectionPromptForMetadata) return '';
    const autoPrompt = autoCorrectPrompt.trim();
    if (autoPrompt) return autoPrompt;
    const manualPrompt = correctionPrompt.trim();
    if (manualPrompt && manualPrompt !== DEFAULT_CORRECTION_PROMPT) return manualPrompt;
    return '';
  }, [autoCorrectPrompt, correctionPrompt, useCorrectionPromptForMetadata]);

  const loadMoreVideos = useCallback(() => {
    if (!hasMoreVideos) return;
    setVisibleCount((prev) => Math.min(prev + PAGE_SIZE, videos.length));
  }, [hasMoreVideos, videos.length]);

  const hasDedicatedPreviewProxy = useCallback((video?: Video | null) => {
    if (video?.has_preview_proxy) return true;
    const previewUrl = String(video?.preview_media_url || '');
    return previewUrl.includes('/proxy_previews/');
  }, []);

  const toneStyle = (tone: 'neutral' | 'good' | 'bad') =>
    tone === 'good' ? styles.statusGood : tone === 'bad' ? styles.statusBad : styles.statusNeutral;

  const processToneStyle = (status?: string) => {
    const key = String(status || '').toLowerCase();
    if (key === 'done') return styles.statusGood;
    if (key === 'error') return styles.statusBad;
    if (key === 'working') return styles.statusWarning;
    return styles.statusNeutral;
  };

  function formatTimestamp(value?: string | null) {
    if (!value) return '';
    try {
      return new Date(value).toLocaleString();
    } catch (_err) {
      return value;
    }
  }

  const queueStatusLabel = (status?: string) => {
    const key = String(status || '').toLowerCase();
    if (key === 'queued') return t('publish_queue_status_queued');
    if (key === 'running') return t('publish_queue_status_running');
    if (key === 'done' || key === 'completed') return t('publish_queue_status_done');
    if (key === 'failed' || key === 'error') return t('publish_queue_status_failed');
    return status || t('publish_queue_status_queued');
  };

  const normalizePublishSelection = useCallback(
    (value: unknown) => {
      const next = { ...defaultPublishSelection };
      if (value && typeof value === 'object' && !Array.isArray(value)) {
        Object.keys(next).forEach((key) => {
          if (key in (value as Record<string, unknown>)) {
            next[key as keyof typeof next] = Boolean((value as Record<string, unknown>)[key]);
          }
        });
      }
      return next;
    },
    [defaultPublishSelection],
  );

  const loadVideos = useCallback(async (silent?: boolean) => {
    if (!silent) setLoadingVideos(true);
    try {
      const resp = await fetch(`${API_URL}/api/videos`);
      const json = await resp.json();
      const items = json.videos || [];
      setVideos(items);
      setVisibleCount((current) => Math.min(Math.max(current, PAGE_SIZE), items.length));
      setSelectedVideoId((current) => {
        if (current && items.some((video: Video) => video.id === current)) return current;
        return items[0]?.id ?? null;
      });
    } catch (_err) {
      // ignore fetch errors
    } finally {
      if (!silent) setLoadingVideos(false);
    }
  }, []);

  const runVisiblePreviewBackfill = useCallback(async () => {
    if (previewProxyRunningRef.current) return;
    previewProxyRunningRef.current = true;
    try {
      while (previewProxyPendingIdsRef.current.length) {
        const nextVideoId = previewProxyPendingIdsRef.current.shift();
        if (!nextVideoId) continue;
        const currentVideo = videosRef.current.find((video) => video.id === nextVideoId);
        if (!currentVideo || hasDedicatedPreviewProxy(currentVideo)) continue;
        try {
          const resp = await fetch(`${API_URL}/api/videos/${nextVideoId}/proxy`, { method: 'POST' });
          const json = await resp.json().catch(() => ({}));
          if (!resp.ok || !json?.media_url) continue;
          setVideos((prev) =>
            prev.map((video) =>
              video.id === nextVideoId
                ? {
                    ...video,
                    preview_media_url: json.media_url,
                    preview_image_url: json.preview_image_url ?? video.preview_image_url ?? null,
                    needs_preview_proxy: Boolean(json.needs_preview_proxy),
                    has_preview_proxy: Boolean(json.has_preview_proxy ?? true),
                    has_preview_image: Boolean(json.has_preview_image ?? json.preview_image_url ?? video.preview_image_url),
                  }
                : video,
            ),
          );
        } catch (_err) {
          // Best-effort only.
        }
      }
    } finally {
      previewProxyRunningRef.current = false;
    }
  }, [hasDedicatedPreviewProxy]);

  const queueVisiblePreviewBackfill = useCallback((items: Video[]) => {
    let shouldRun = false;
    for (const video of items) {
      if (!video?.id || hasDedicatedPreviewProxy(video) || !video.needs_preview_proxy) continue;
      if (previewProxyAttemptedIdsRef.current.has(video.id)) continue;
      previewProxyAttemptedIdsRef.current.add(video.id);
      previewProxyPendingIdsRef.current.push(video.id);
      shouldRun = true;
    }
    if (shouldRun) {
      void runVisiblePreviewBackfill();
    }
  }, [hasDedicatedPreviewProxy, runVisiblePreviewBackfill]);

  const onViewableItemsChanged = useRef(
    ({ viewableItems }: { viewableItems: ViewToken[] }) => {
      const items = viewableItems
        .map((entry) => entry.item as Video | null | undefined)
        .filter((item): item is Video => Boolean(item));
      queueVisiblePreviewBackfillRef.current(items);
    },
  ).current;

  const loadPublishSettings = useCallback(async () => {
    try {
      const resp = await fetch(`${API_URL}/api/ui-settings/publish_platforms`);
      const json = await resp.json();
      if (resp.ok) {
        setSelected(normalizePublishSelection(json?.value));
      }
    } catch (_err) {
      // ignore
    } finally {
      setPublishSettingsLoaded(true);
    }
  }, [normalizePublishSelection]);

  const loadPublishOptions = useCallback(async () => {
    try {
      const [optionsResp, languagesResp, burnLayoutResp] = await Promise.all([
        fetch(`${API_URL}/api/ui-settings/publish_options`),
        fetch(`${API_URL}/api/ui-settings/translation_languages`),
        fetch(`${API_URL}/api/ui-settings/burn_layout`),
      ]);
      let nextLanguages: string[] = DEFAULT_TRANSLATION_LANGUAGES;
      if (languagesResp.ok) {
        const languagesJson = await languagesResp.json();
        if (Array.isArray(languagesJson?.value) && languagesJson.value.length) {
          nextLanguages = languagesJson.value
            .map((lang: unknown) => String(lang))
            .filter((lang: string) => AVAILABLE_TRANSLATION_LANGUAGES.includes(lang));
          if (!nextLanguages.length) nextLanguages = DEFAULT_TRANSLATION_LANGUAGES;
        }
      }
      if (optionsResp.ok) {
        const optionsJson = await optionsResp.json();
        const value = optionsJson?.value || {};
        if (typeof value.burnSubtitles === 'boolean') {
          setBurnSubtitles(value.burnSubtitles);
        }
        if (value.subtitleSourceVersion === 'original') {
          setUsePolishedSubtitles(false);
        } else if (value.subtitleSourceVersion === 'polished') {
          setUsePolishedSubtitles(true);
        } else {
          setUsePolishedSubtitles(true);
        }
        setUseCorrectionPromptForMetadata(value.useCorrectionPromptForMetadata !== false);
        if (Array.isArray(value.translationLanguages) && value.translationLanguages.length) {
          const cleaned = value.translationLanguages
            .map((lang: unknown) => String(lang))
            .filter((lang: string) => AVAILABLE_TRANSLATION_LANGUAGES.includes(lang));
          if (cleaned.length) nextLanguages = cleaned;
        }
      }
      if (burnLayoutResp.ok) {
        const burnLayoutJson = await burnLayoutResp.json();
        const liftRatio = normalizeSubtitleLiftRatio(burnLayoutJson?.value?.liftRatio);
        const rows = normalizeSubtitleRows(burnLayoutJson?.value?.rows);
        const fontScale = normalizeSubtitleFontScale(burnLayoutJson?.value?.fontScale);
        setSubtitleLiftRatio(liftRatio);
        setSubtitleLiftInput(formatSubtitleLiftRatio(liftRatio));
        setSubtitleRows(rows);
        setSubtitleRowsInput(String(rows));
        setSubtitleFontScale(fontScale);
        setSubtitleFontScaleInput(formatSubtitleFontScale(fontScale));
        setSubtitleFontBold(burnLayoutJson?.value?.fontBold !== false);
        setSubtitleFontColor(normalizeHexColor(burnLayoutJson?.value?.fontColor, DEFAULT_SUBTITLE_FONT_COLOR));
        setSubtitleOutlineBold(burnLayoutJson?.value?.outlineBold !== false);
        setSubtitleOutlineColor(normalizeHexColor(burnLayoutJson?.value?.outlineColor, DEFAULT_SUBTITLE_OUTLINE_COLOR));
        const portraitValue = burnLayoutJson?.value?.portraitBlurFill || {};
        const nextPortraitY = normalizePortraitForegroundY(portraitValue?.foregroundY);
        const nextPortraitBottomSpace = normalizePortraitBottomSpaceRatio(portraitValue?.bottomSpaceRatio);
        setPortraitBlurFill(Boolean(portraitValue?.enabled));
        setPortraitBlurMode(normalizePortraitMode(portraitValue?.mode));
        setPortraitForegroundY(nextPortraitY);
        setPortraitForegroundYInput(String(nextPortraitY));
        setPortraitBottomSpaceRatio(nextPortraitBottomSpace);
        setPortraitBottomSpaceInput(formatPortraitBottomSpaceRatio(nextPortraitBottomSpace));
      }
      setTranslationLanguages(nextLanguages.slice(0, AVAILABLE_TRANSLATION_LANGUAGES.length));
    } catch (_err) {
      // ignore
    } finally {
      setPublishOptionsLoaded(true);
    }
  }, []);

  const persistBurnLayout = useCallback(async (updates: {
    liftRatio?: number;
    rows?: number;
    fontScale?: number;
    fontBold?: boolean;
    fontColor?: string;
    outlineBold?: boolean;
    outlineColor?: string;
    portraitBlurFill?: {
      enabled?: boolean;
      mode?: PortraitBlurMode;
      foregroundY?: number;
      bottomSpaceRatio?: number;
    };
  }) => {
    try {
      let existing = {};
      const resp = await fetch(`${API_URL}/api/ui-settings/burn_layout`);
      if (resp.ok) {
        const json = await resp.json().catch(() => ({}));
        if (json?.value && typeof json.value === 'object') existing = json.value;
      }
      await fetch(`${API_URL}/api/ui-settings/burn_layout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...existing,
          ...(updates.liftRatio === undefined ? {} : { liftRatio: normalizeSubtitleLiftRatio(updates.liftRatio) }),
          ...(updates.rows === undefined ? {} : { rows: normalizeSubtitleRows(updates.rows) }),
          ...(updates.fontScale === undefined ? {} : { fontScale: normalizeSubtitleFontScale(updates.fontScale) }),
          ...(updates.fontBold === undefined ? {} : { fontBold: Boolean(updates.fontBold) }),
          ...(updates.fontColor === undefined
            ? {}
            : { fontColor: normalizeHexColor(updates.fontColor, subtitleFontColor) }),
          ...(updates.outlineBold === undefined ? {} : { outlineBold: Boolean(updates.outlineBold) }),
          ...(updates.outlineColor === undefined
            ? {}
            : { outlineColor: normalizeHexColor(updates.outlineColor, subtitleOutlineColor) }),
          ...(updates.portraitBlurFill === undefined
            ? {}
            : {
                portraitBlurFill: {
                  ...((existing as any)?.portraitBlurFill || {}),
                  ...updates.portraitBlurFill,
                  ...(updates.portraitBlurFill.foregroundY === undefined
                    ? {}
                    : { foregroundY: normalizePortraitForegroundY(updates.portraitBlurFill.foregroundY) }),
                  ...(updates.portraitBlurFill.bottomSpaceRatio === undefined
                    ? {}
                    : {
                        bottomSpaceRatio: normalizePortraitBottomSpaceRatio(
                          updates.portraitBlurFill.bottomSpaceRatio,
                        ),
                      }),
                },
              }),
          liftSlots: 0,
        }),
      });
    } catch (_err) {
      // ignore
    }
  }, [subtitleFontColor, subtitleOutlineColor]);

  const setAndPersistSubtitleLiftRatio = useCallback(
    (value: unknown) => {
      const nextLiftRatio = normalizeSubtitleLiftRatio(value, subtitleLiftRatio);
      setSubtitleLiftRatio(nextLiftRatio);
      setSubtitleLiftInput(formatSubtitleLiftRatio(nextLiftRatio));
      void persistBurnLayout({ liftRatio: nextLiftRatio });
      return nextLiftRatio;
    },
    [persistBurnLayout, subtitleLiftRatio],
  );

  const commitSubtitleLiftRatio = useCallback(async () => {
    const nextLiftRatio = normalizeSubtitleLiftRatio(subtitleLiftInput, subtitleLiftRatio);
    setSubtitleLiftRatio(nextLiftRatio);
    setSubtitleLiftInput(formatSubtitleLiftRatio(nextLiftRatio));
    await persistBurnLayout({ liftRatio: nextLiftRatio });
    return nextLiftRatio;
  }, [persistBurnLayout, subtitleLiftInput, subtitleLiftRatio]);

  const adjustSubtitleLiftRatio = useCallback(
    (delta: number) => {
      setAndPersistSubtitleLiftRatio(Math.round((subtitleLiftRatio + delta) * 1000) / 1000);
    },
    [setAndPersistSubtitleLiftRatio, subtitleLiftRatio],
  );

  const setAndPersistSubtitleRows = useCallback(
    (value: unknown) => {
      const nextRows = normalizeSubtitleRows(value, subtitleRows);
      setSubtitleRows(nextRows);
      setSubtitleRowsInput(String(nextRows));
      void persistBurnLayout({ rows: nextRows });
      return nextRows;
    },
    [persistBurnLayout, subtitleRows],
  );

  const commitSubtitleRows = useCallback(async () => {
    const nextRows = normalizeSubtitleRows(subtitleRowsInput, subtitleRows);
    setSubtitleRows(nextRows);
    setSubtitleRowsInput(String(nextRows));
    await persistBurnLayout({ rows: nextRows });
    return nextRows;
  }, [persistBurnLayout, subtitleRows, subtitleRowsInput]);

  const adjustSubtitleRows = useCallback(
    (delta: number) => {
      setAndPersistSubtitleRows(subtitleRows + delta);
    },
    [setAndPersistSubtitleRows, subtitleRows],
  );

  const setAndPersistSubtitleFontScale = useCallback(
    (value: unknown) => {
      const nextFontScale = normalizeSubtitleFontScale(value, subtitleFontScale);
      setSubtitleFontScale(nextFontScale);
      setSubtitleFontScaleInput(formatSubtitleFontScale(nextFontScale));
      void persistBurnLayout({ fontScale: nextFontScale });
      return nextFontScale;
    },
    [persistBurnLayout, subtitleFontScale],
  );

  const commitSubtitleFontScale = useCallback(async () => {
    const nextFontScale = normalizeSubtitleFontScale(subtitleFontScaleInput, subtitleFontScale);
    setSubtitleFontScale(nextFontScale);
    setSubtitleFontScaleInput(formatSubtitleFontScale(nextFontScale));
    await persistBurnLayout({ fontScale: nextFontScale });
    return nextFontScale;
  }, [persistBurnLayout, subtitleFontScale, subtitleFontScaleInput]);

  const adjustSubtitleFontScale = useCallback(
    (delta: number) => {
      setAndPersistSubtitleFontScale(Math.round((subtitleFontScale + delta) * 100) / 100);
    },
    [setAndPersistSubtitleFontScale, subtitleFontScale],
  );

  const updateSubtitleFontBold = useCallback(
    (value: boolean) => {
      setSubtitleFontBold(value);
      void persistBurnLayout({ fontBold: value });
    },
    [persistBurnLayout],
  );

  const updateSubtitleOutlineBold = useCallback(
    (value: boolean) => {
      setSubtitleOutlineBold(value);
      void persistBurnLayout({ outlineBold: value });
    },
    [persistBurnLayout],
  );

  const commitSubtitleFontColor = useCallback(async () => {
    const nextColor = normalizeHexColor(subtitleFontColor, DEFAULT_SUBTITLE_FONT_COLOR);
    setSubtitleFontColor(nextColor);
    await persistBurnLayout({ fontColor: nextColor });
    return nextColor;
  }, [persistBurnLayout, subtitleFontColor]);

  const commitSubtitleOutlineColor = useCallback(async () => {
    const nextColor = normalizeHexColor(subtitleOutlineColor, DEFAULT_SUBTITLE_OUTLINE_COLOR);
    setSubtitleOutlineColor(nextColor);
    await persistBurnLayout({ outlineColor: nextColor });
    return nextColor;
  }, [persistBurnLayout, subtitleOutlineColor]);

  const updatePortraitBlurFill = useCallback(
    (value: boolean) => {
      setPortraitBlurFill(value);
      void persistBurnLayout({
        portraitBlurFill: {
          enabled: value,
          mode: portraitBlurMode,
          foregroundY: portraitForegroundY,
          bottomSpaceRatio: portraitBottomSpaceRatio,
        },
      });
    },
    [persistBurnLayout, portraitBlurMode, portraitBottomSpaceRatio, portraitForegroundY],
  );

  const updatePortraitBlurMode = useCallback(
    (mode: PortraitBlurMode) => {
      setPortraitBlurMode(mode);
      void persistBurnLayout({
        portraitBlurFill: {
          enabled: portraitBlurFill,
          mode,
          foregroundY: portraitForegroundY,
          bottomSpaceRatio: portraitBottomSpaceRatio,
        },
      });
    },
    [persistBurnLayout, portraitBlurFill, portraitBottomSpaceRatio, portraitForegroundY],
  );

  const commitPortraitForegroundY = useCallback(async () => {
    const nextY = normalizePortraitForegroundY(portraitForegroundYInput, portraitForegroundY);
    setPortraitForegroundY(nextY);
    setPortraitForegroundYInput(String(nextY));
    await persistBurnLayout({
      portraitBlurFill: {
        enabled: portraitBlurFill,
        mode: portraitBlurMode,
        foregroundY: nextY,
        bottomSpaceRatio: portraitBottomSpaceRatio,
      },
    });
    return nextY;
  }, [
    persistBurnLayout,
    portraitBlurFill,
    portraitBlurMode,
    portraitBottomSpaceRatio,
    portraitForegroundY,
    portraitForegroundYInput,
  ]);

  const commitPortraitBottomSpaceRatio = useCallback(async () => {
    const nextBottomSpace = normalizePortraitBottomSpaceRatio(portraitBottomSpaceInput, portraitBottomSpaceRatio);
    setPortraitBottomSpaceRatio(nextBottomSpace);
    setPortraitBottomSpaceInput(formatPortraitBottomSpaceRatio(nextBottomSpace));
    await persistBurnLayout({
      portraitBlurFill: {
        enabled: portraitBlurFill,
        mode: portraitBlurMode,
        foregroundY: portraitForegroundY,
        bottomSpaceRatio: nextBottomSpace,
      },
    });
    return nextBottomSpace;
  }, [
    persistBurnLayout,
    portraitBlurFill,
    portraitBlurMode,
    portraitBottomSpaceInput,
    portraitBottomSpaceRatio,
    portraitForegroundY,
  ]);

  const commitSubtitleBurnLayoutSettings = useCallback(async () => {
    const nextLiftRatio = normalizeSubtitleLiftRatio(subtitleLiftInput, subtitleLiftRatio);
    const nextRows = normalizeSubtitleRows(subtitleRowsInput, subtitleRows);
    const nextFontScale = normalizeSubtitleFontScale(subtitleFontScaleInput, subtitleFontScale);
    const nextFontColor = normalizeHexColor(subtitleFontColor, DEFAULT_SUBTITLE_FONT_COLOR);
    const nextOutlineColor = normalizeHexColor(subtitleOutlineColor, DEFAULT_SUBTITLE_OUTLINE_COLOR);
    const nextPortraitY = normalizePortraitForegroundY(portraitForegroundYInput, portraitForegroundY);
    const nextPortraitBottomSpace = normalizePortraitBottomSpaceRatio(
      portraitBottomSpaceInput,
      portraitBottomSpaceRatio,
    );
    setSubtitleLiftRatio(nextLiftRatio);
    setSubtitleLiftInput(formatSubtitleLiftRatio(nextLiftRatio));
    setSubtitleRows(nextRows);
    setSubtitleRowsInput(String(nextRows));
    setSubtitleFontScale(nextFontScale);
    setSubtitleFontScaleInput(formatSubtitleFontScale(nextFontScale));
    setSubtitleFontColor(nextFontColor);
    setSubtitleOutlineColor(nextOutlineColor);
    setPortraitForegroundY(nextPortraitY);
    setPortraitForegroundYInput(String(nextPortraitY));
    setPortraitBottomSpaceRatio(nextPortraitBottomSpace);
    setPortraitBottomSpaceInput(formatPortraitBottomSpaceRatio(nextPortraitBottomSpace));
    const nextPortraitBlurFill = {
      enabled: portraitBlurFill,
      mode: portraitBlurMode,
      foregroundY: nextPortraitY,
      bottomSpaceRatio: nextPortraitBottomSpace,
    };
    await persistBurnLayout({
      liftRatio: nextLiftRatio,
      rows: nextRows,
      fontScale: nextFontScale,
      fontBold: subtitleFontBold,
      fontColor: nextFontColor,
      outlineBold: subtitleOutlineBold,
      outlineColor: nextOutlineColor,
      portraitBlurFill: nextPortraitBlurFill,
    });
    return {
      liftRatio: nextLiftRatio,
      rows: nextRows,
      fontScale: nextFontScale,
      fontBold: subtitleFontBold,
      fontColor: nextFontColor,
      outlineBold: subtitleOutlineBold,
      outlineColor: nextOutlineColor,
      portraitBlurFill: nextPortraitBlurFill,
    };
  }, [
    persistBurnLayout,
    portraitBlurFill,
    portraitBlurMode,
    portraitBottomSpaceInput,
    portraitBottomSpaceRatio,
    portraitForegroundY,
    portraitForegroundYInput,
    subtitleFontBold,
    subtitleFontColor,
    subtitleFontScale,
    subtitleFontScaleInput,
    subtitleLiftInput,
    subtitleLiftRatio,
    subtitleOutlineBold,
    subtitleOutlineColor,
    subtitleRows,
    subtitleRowsInput,
  ]);

  const persistPublishOptions = useCallback(async (
    nextBurn: boolean,
    nextLanguages: string[],
    nextUsePolished = usePolishedSubtitles,
    nextUseCorrectionPromptForMetadata = useCorrectionPromptForMetadata,
  ) => {
    try {
      await fetch(`${API_URL}/api/ui-settings/publish_options`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          burnSubtitles: nextBurn,
          translationLanguages: nextLanguages,
          usePolishedSubtitles: nextUsePolished,
          useCorrectionPromptForMetadata: nextUseCorrectionPromptForMetadata,
          subtitleSourceVersion: nextUsePolished ? 'polished' : 'original',
          publicationMode: 'override',
        }),
      });
    } catch (_err) {
      // ignore
    }
  }, [useCorrectionPromptForMetadata, usePolishedSubtitles]);

  const toggleTranslationLanguage = useCallback(
    (language: string) => {
      const active = translationLanguages.includes(language);
      if (active && translationLanguages.length <= 1) return;
      const nextLanguages = active
        ? translationLanguages.filter((candidate) => candidate !== language)
        : [...translationLanguages, language].filter((candidate, index, all) => all.indexOf(candidate) === index);
      setTranslationLanguages(nextLanguages);
      void persistPublishOptions(burnSubtitles, nextLanguages);
    },
    [burnSubtitles, persistPublishOptions, translationLanguages],
  );

  const updateBurnSubtitles = useCallback(
    (value: boolean) => {
      setBurnSubtitles(value);
      void persistPublishOptions(value, translationLanguages);
    },
    [persistPublishOptions, translationLanguages],
  );

  const selectSubtitleSource = useCallback(
    (source: SubtitleSourceVariant) => {
      const nextUsePolished = source === 'polished';
      setUsePolishedSubtitles(nextUsePolished);
      setSubtitleSourceMenuOpen(false);
      void persistPublishOptions(burnSubtitles, translationLanguages, nextUsePolished);
    },
    [burnSubtitles, persistPublishOptions, translationLanguages],
  );

  const updateUseCorrectionPromptForMetadata = useCallback(
    (value: boolean) => {
      setUseCorrectionPromptForMetadata(value);
      void persistPublishOptions(burnSubtitles, translationLanguages, usePolishedSubtitles, value);
    },
    [burnSubtitles, persistPublishOptions, translationLanguages, usePolishedSubtitles],
  );

  const openAutoCorrectPrompt = useCallback(() => {
    setAutoCorrectDraftPrompt(autoCorrectPrompt);
    setAutoCorrectPromptError('');
    setAutoCorrectPromptOpen(true);
  }, [autoCorrectPrompt]);

  const updateAutoCorrectSubtitles = useCallback(
    (value: boolean) => {
      if (!value) {
        setAutoCorrectSubtitles(false);
        return;
      }
      openAutoCorrectPrompt();
    },
    [openAutoCorrectPrompt],
  );

  const cancelAutoCorrectPrompt = useCallback(() => {
    setAutoCorrectPromptOpen(false);
    setAutoCorrectPromptError('');
    if (!autoCorrectPrompt.trim()) {
      setAutoCorrectSubtitles(false);
    }
  }, [autoCorrectPrompt]);

  const saveAutoCorrectPrompt = useCallback(() => {
    const trimmed = autoCorrectDraftPrompt.trim();
    if (!trimmed) {
      setAutoCorrectPromptError(t('publish_auto_correct_prompt_required'));
      setAutoCorrectSubtitles(false);
      return;
    }
    setAutoCorrectPrompt(trimmed);
    setAutoCorrectSubtitles(true);
    setUsePolishedSubtitles(true);
    void persistPublishOptions(burnSubtitles, translationLanguages, true);
    setAutoCorrectPromptError('');
    setAutoCorrectPromptOpen(false);
  }, [autoCorrectDraftPrompt, burnSubtitles, persistPublishOptions, t, translationLanguages]);

  const selectPublicationRun = useCallback((key: string) => {
    setRunSelectionTouched(true);
    setProcessRunMenuOpen(false);
    setPublishRunMenuOpen(false);
    if (key === 'new') {
      setPublishAsNewSession(true);
      setPublicationSessionId(null);
      return;
    }
    setPublishAsNewSession(false);
    if (key.startsWith('session:')) {
      const id = Number(key.slice('session:'.length));
      setPublicationSessionId(Number.isFinite(id) && id > 0 ? id : null);
    } else {
      setPublicationSessionId(null);
    }
  }, []);

  const fetchLogoSettings = useCallback(async (): Promise<LogoSettings | null> => {
    try {
      const resp = await fetch(`${API_URL}/api/ui-settings/logo_settings`);
      const json = await resp.json();
      if (!resp.ok) return null;
      const value = json?.value;
      if (!value?.logoPath) return null;
      const enabled = typeof value.enabled === 'boolean' ? value.enabled : Boolean(value.logoPath);
      return { ...value, enabled };
    } catch (_err) {
      return null;
    }
  }, []);

  const loadPublishQueue = useCallback(async (silent?: boolean) => {
    if (!silent) setQueueLoading(true);
    try {
      const resp = await fetch(`${API_URL}/api/autopublish/queue`);
      const json = await resp.json();
      if (!resp.ok) {
        setQueueError(`${t('publish_queue_failed')}: ${json?.error || resp.statusText}`);
        return;
      }
      if (json?.status === 'unavailable') {
        setPublishQueue([]);
        setQueueError(t('publish_queue_unavailable'));
        return;
      }
      const jobs = Array.isArray(json?.jobs) ? json.jobs : [];
      setPublishQueue(jobs);
      setQueueError('');
    } catch (_err) {
      setQueueError(t('publish_queue_failed'));
    } finally {
      if (!silent) setQueueLoading(false);
    }
  }, [t]);

  const confirmDeleteSelectedVideo = useCallback(async () => {
    if (!confirmDeleteVideo || deleteVideoPending) return;
    const deletingId = confirmDeleteVideo.id;
    const deletingPath = confirmDeleteVideo.file_path;
    setDeleteVideoPending(true);
    setDeleteVideoError('');
    try {
      const resp = await fetch(`${API_URL}/api/videos/${deletingId}`, { method: 'DELETE' });
      const payload = await resp.json().catch(() => ({}));
      if (!resp.ok) {
        throw new Error(payload?.error || 'Delete failed');
      }
      const remainingVideos = videosRef.current.filter(
        (video) => video.id !== deletingId && video.file_path !== deletingPath,
      );
      setVideos(remainingVideos);
      setVisibleCount((current) => Math.min(Math.max(current, PAGE_SIZE), remainingVideos.length));
      setSelectedVideoId((current) => {
        if (current && current !== deletingId && remainingVideos.some((video) => video.id === current)) {
          return current;
        }
        return remainingVideos[0]?.id ?? null;
      });
      setConfirmDeleteVideo(null);
      await loadVideos(true);
      await loadPublishQueue(true);
      triggerStudioRefresh();
    } catch (err) {
      setDeleteVideoError(err instanceof Error ? err.message : 'Delete failed');
    } finally {
      setDeleteVideoPending(false);
    }
  }, [confirmDeleteVideo, deleteVideoPending, loadPublishQueue, loadVideos]);

  const requestCoverExtraction = useCallback(async (
    videoId: number,
    sessionId: number | null = null,
    silent = false,
  ): Promise<boolean> => {
    if (!videoId) return false;
    const requestId = ++coverRequestIdRef.current;
    setCoverLoading(true);
    if (!silent) {
      setCoverStatus(t('publish_cover_extracting'));
      setCoverTone('neutral');
    }
    try {
      const body: Record<string, unknown> = { lang: 'zh' };
      if (sessionId) body.publicationSessionId = sessionId;
      const resp = await fetch(`${API_URL}/api/videos/${videoId}/cover`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const json = await resp.json().catch(() => ({}));
      if (requestId !== coverRequestIdRef.current) return false;
      if (!resp.ok) {
        setCoverUrl(null);
        if (!silent) {
          setCoverStatus(`${t('publish_cover_failed')}: ${json.error || json.details || resp.statusText}`);
          setCoverTone('bad');
        }
        return false;
      }
      if (json.cover_url) {
        setCoverUrl(withCacheBust(`${API_URL}${json.cover_url}`));
      }
      setCoverStatus(t('publish_cover_ready'));
      setCoverTone('good');
      return true;
    } catch (err: any) {
      if (requestId === coverRequestIdRef.current) {
        setCoverUrl(null);
        if (!silent) {
          setCoverStatus(`${t('publish_cover_failed')}: ${err?.message || String(err)}`);
          setCoverTone('bad');
        }
      }
      return false;
    } finally {
      if (requestId === coverRequestIdRef.current) {
        setCoverLoading(false);
      }
    }
  }, [t]);

  const loadCoverPreview = useCallback(async (
    videoId: number,
    sessionId: number | null = null,
    autoExtract = false,
  ): Promise<boolean> => {
    const requestId = ++coverRequestIdRef.current;
    try {
      const suffix = sessionId ? `?publicationSessionId=${encodeURIComponent(String(sessionId))}` : '';
      const resp = await fetch(`${API_URL}/api/videos/${videoId}/cover${suffix}`);
      const json = await resp.json().catch(() => ({}));
      if (requestId !== coverRequestIdRef.current) return false;
      if (resp.ok && json.cover_url) {
        setCoverUrl(withCacheBust(`${API_URL}${json.cover_url}`));
        setCoverStatus('');
        setCoverTone('neutral');
        return true;
      }
      setCoverUrl(null);
      if (resp.status === 404 && autoExtract) {
        return requestCoverExtraction(videoId, sessionId, false);
      }
      return false;
    } catch (_err) {
      if (requestId === coverRequestIdRef.current) {
        setCoverUrl(null);
      }
      return false;
    }
  }, [requestCoverExtraction]);

  const loadBaseBurnPreview = useCallback(async (videoId: number) => {
    try {
      const resp = await fetch(`${API_URL}/api/videos/${videoId}/burn-subtitles`);
      const json = await resp.json().catch(() => ({}));
      if (!resp.ok) {
        setBaseBurnPreviewUrl(null);
        setBaseBurnPreviewStatus(null);
        return;
      }
      setBaseBurnPreviewStatus(json?.status || null);
      setBaseBurnPreviewUrl(json?.output_url ? resolveMediaSrc(json.output_url) : null);
    } catch (_err) {
      setBaseBurnPreviewUrl(null);
      setBaseBurnPreviewStatus(null);
    }
  }, [resolveMediaSrc]);

  const loadProcessStatus = useCallback(
    async (videoId: number, silent?: boolean) => {
      if (!silent) setProcessStatusLoading(true);
      try {
        const suffix = publicationSessionId ? `?publicationSessionId=${publicationSessionId}` : '';
        const resp = await fetch(`${API_URL}/api/videos/${videoId}/process-status${suffix}`);
        const json = await resp.json().catch(() => ({}));
        if (!resp.ok) {
          setProcessStatusError(json?.error || resp.statusText);
          setProcessSteps(null);
          setProcessUpdatedAt(null);
          setProcessReadyForCover(false);
          setProcessReadyForPublish(false);
          return null;
        }
        setProcessSteps(json?.steps || null);
        setProcessUpdatedAt(json?.updated_at || null);
        setProcessReadyForCover(Boolean(json?.ready_for_cover));
        setProcessReadyForPublish(Boolean(json?.ready_for_publish));
        setProcessStatusError('');
        return json;
      } catch (err: any) {
        setProcessStatusError(err?.message || String(err));
        setProcessSteps(null);
        setProcessUpdatedAt(null);
        setProcessReadyForCover(false);
        setProcessReadyForPublish(false);
        return null;
      } finally {
        if (!silent) setProcessStatusLoading(false);
      }
    },
    [publicationSessionId],
  );

  const loadPublicationSessions = useCallback(async (videoId: number, defaultToLatest = false) => {
    setSessionLoading(true);
    try {
      const resp = await fetch(`${API_URL}/api/videos/${videoId}/publication-sessions`);
      const json = await resp.json().catch(() => ({}));
      if (resp.ok && Array.isArray(json?.sessions)) {
        const sessions = json.sessions as PublicationSession[];
        setPublicationSessions(sessions);
        const selectedExists = publicationSessionId
          ? sessions.some((session) => session.id === publicationSessionId)
          : false;
        if (publishAsNewSession) {
          return;
        }
        if ((defaultToLatest || !runSelectionTouched) && sessions.length) {
          setPublicationSessionId(sessions[0].id);
          return;
        }
        if (publicationSessionId && !selectedExists) {
          setPublicationSessionId(sessions[0]?.id ?? null);
        }
      }
    } catch (_err) {
      // ignore
    } finally {
      setSessionLoading(false);
    }
  }, [publicationSessionId, publishAsNewSession, runSelectionTouched]);

  const createPublicationSession = useCallback(async (): Promise<number | null> => {
    if (!selectedVideoId) return null;
    const resp = await fetch(`${API_URL}/api/videos/${selectedVideoId}/publication-sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: `Publication ${new Date().toLocaleString()}`,
        mode: 'new',
        config: {
          burnSubtitles,
          translationLanguages,
          usePolishedSubtitles,
          publicationMode: 'new',
        },
      }),
    });
    const json = await resp.json().catch(() => ({}));
    if (!resp.ok) throw new Error(json?.error || resp.statusText);
    const id = Number(json?.session?.id || 0);
    if (id > 0) {
      setPublishAsNewSession(false);
      setRunSelectionTouched(true);
      setPublicationSessionId(id);
      await loadPublicationSessions(selectedVideoId, true);
      return id;
    }
    return null;
  }, [burnSubtitles, loadPublicationSessions, selectedVideoId, translationLanguages, usePolishedSubtitles]);

  const deletePublicationSession = useCallback(async (sessionId: number) => {
    if (!selectedVideoId) return;
    setSessionLoading(true);
    try {
      await fetch(`${API_URL}/api/videos/${selectedVideoId}/publication-sessions/${sessionId}`, {
        method: 'DELETE',
      });
      if (publicationSessionId === sessionId) setPublicationSessionId(null);
      await loadPublicationSessions(selectedVideoId, true);
      await loadProcessStatus(selectedVideoId, true);
    } finally {
      setSessionLoading(false);
    }
  }, [loadProcessStatus, loadPublicationSessions, publicationSessionId, selectedVideoId]);

  const loadSubtitleCorrection = useCallback(async () => {
    if (!selectedVideoId) return;
    setCorrectionLoading(true);
    setCorrectionStatus('');
    try {
      const resp = await fetch(`${API_URL}/api/videos/${selectedVideoId}/subtitle-correction`);
      const json = (await resp.json().catch(() => ({}))) as SubtitleCorrectionPayload & { error?: string };
      if (!resp.ok) {
        setCorrectionStatus(json?.error || resp.statusText);
        return;
      }
      setOriginalSubtitleText(json.original?.text || '');
      setPolishedSubtitleText(json.polished?.text || json.original?.text || '');
    } catch (err: any) {
      setCorrectionStatus(err?.message || String(err));
    } finally {
      setCorrectionLoading(false);
    }
  }, [selectedVideoId]);

  const openSubtitleCorrection = useCallback(() => {
    setCorrectionOpen(true);
    void loadSubtitleCorrection();
  }, [loadSubtitleCorrection]);

  const runCorrectionAction = useCallback(async (action: 'ai' | 'save_original' | 'save_polished') => {
    if (!selectedVideoId || correctionSaving) return;
    setCorrectionSaving(true);
    setCorrectionStatus('');
    try {
      const text = action === 'save_original' ? originalSubtitleText : polishedSubtitleText;
      const resp = await fetch(`${API_URL}/api/videos/${selectedVideoId}/subtitle-correction`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action,
          prompt: correctionPrompt,
          text,
          sourceVariant: correctionSourceVariant,
        }),
      });
      const json = (await resp.json().catch(() => ({}))) as SubtitleCorrectionPayload & { error?: string };
      if (!resp.ok) {
        setCorrectionStatus(json?.error || resp.statusText);
        return;
      }
      setOriginalSubtitleText(json.original?.text || originalSubtitleText);
      setPolishedSubtitleText(json.polished?.text || polishedSubtitleText || json.original?.text || '');
      setCorrectionStatus(
        action === 'ai' ? t('publish_correction_ai_saved') : t('publish_correction_saved'),
      );
      await loadProcessStatus(selectedVideoId, true);
    } catch (err: any) {
      setCorrectionStatus(err?.message || String(err));
    } finally {
      setCorrectionSaving(false);
    }
  }, [
    correctionPrompt,
    correctionSaving,
    correctionSourceVariant,
    loadProcessStatus,
    originalSubtitleText,
    polishedSubtitleText,
    selectedVideoId,
    t,
  ]);

  const updateSourceVideoDimensionsFromEvent = useCallback((event: any) => {
    const target = event?.currentTarget;
    const width = Number(target?.videoWidth || 0);
    const height = Number(target?.videoHeight || 0);
    if (width > 0 && height > 0) {
      setSourceVideoDimensions({ width, height });
    }
  }, []);

  useEffect(() => {
    loadVideos();
  }, [loadVideos]);

  useEffect(() => {
    videosRef.current = videos;
  }, [videos]);

  useEffect(() => {
    queueVisiblePreviewBackfillRef.current = queueVisiblePreviewBackfill;
  }, [queueVisiblePreviewBackfill]);

  useEffect(() => {
    const interval = setInterval(() => {
      loadVideos(true);
    }, 15000);
    return () => clearInterval(interval);
  }, [loadVideos]);

  useEffect(() => {
    loadPublishSettings();
  }, [loadPublishSettings]);

  useEffect(() => {
    loadPublishOptions();
  }, [loadPublishOptions]);

  useEffect(() => {
    setSourceVideoDimensions(null);
    setPortraitLayoutModalOpen(false);
  }, [previewVideoUrl, selectedVideoId]);

  useEffect(() => {
    if (!publishSettingsLoaded) return;
    const persist = async () => {
      try {
        await fetch(`${API_URL}/api/ui-settings/publish_platforms`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(selected),
        });
      } catch (_err) {
        // ignore
      }
    };
    persist();
  }, [publishSettingsLoaded, selected]);

  useEffect(() => {
    loadPublishQueue();
    const interval = setInterval(() => {
      loadPublishQueue(true);
    }, 5000);
    return () => clearInterval(interval);
  }, [loadPublishQueue]);

  useEffect(() => {
    const unsubscribe = subscribeStudioRefresh(() => {
      loadVideos(true);
    });
    return unsubscribe;
  }, [loadVideos]);

  useEffect(() => {
    if (!hasMoreVideos) return;
    if (!listHeight || !listContentHeight) return;
    if (listContentHeight <= listHeight) {
      loadMoreVideos();
    }
  }, [hasMoreVideos, listHeight, listContentHeight, loadMoreVideos]);

  useEffect(() => {
    if (!selectedVideoId) return;
    setCoverUrl(null);
    setCoverStatus('');
    setCoverTone('neutral');
    setProcessStatus('');
    setProcessTone('neutral');
    setProcessRunning(false);
    setProcessSteps(null);
    setProcessUpdatedAt(null);
    setProcessReadyForCover(false);
    setProcessReadyForPublish(false);
    setProcessStatusError('');
    setPublishStatus('');
    setPublishTone('neutral');
    setPublishZipUrl(null);
    setPublishAsNewSession(false);
    setPublicationSessionId(null);
    setPublicationSessions([]);
    setRunSelectionTouched(false);
    setProcessRunMenuOpen(false);
    setPublishRunMenuOpen(false);
    setPreviewSourceKey('original');
    setPreviewSourceMenuOpen(false);
    setBaseBurnPreviewUrl(null);
    setBaseBurnPreviewStatus(null);
    setCorrectionOpen(false);
    setOriginalSubtitleText('');
    setPolishedSubtitleText('');
    loadBaseBurnPreview(selectedVideoId);
    loadPublicationSessions(selectedVideoId, true);
    loadProcessStatus(selectedVideoId, true);
  }, [selectedVideoId]);

  useEffect(() => {
    if (!selectedVideoId) return;
    setCoverUrl(null);
    setCoverStatus('');
    setCoverTone('neutral');
    void loadCoverPreview(selectedVideoId, selectedCoverSessionId, processReadyForCover);
  }, [loadCoverPreview, processReadyForCover, selectedCoverSessionId, selectedVideoId]);

  useEffect(() => {
    if (!selectedVideoId) return;
    loadProcessStatus(selectedVideoId, true);
    const interval = setInterval(() => {
      loadProcessStatus(selectedVideoId, true);
    }, 5000);
    return () => clearInterval(interval);
  }, [selectedVideoId, loadProcessStatus]);

  useEffect(() => {
    if (!selectedVideo) return;
    queueVisiblePreviewBackfill([selectedVideo]);
  }, [queueVisiblePreviewBackfill, selectedVideo]);

  useEffect(() => {
    if (!selectedVideoId) return;
    const burnStatus = String(processSteps?.burn?.status || '').toLowerCase();
    if (burnStatus !== 'done') return;
    loadBaseBurnPreview(selectedVideoId);
    loadPublicationSessions(selectedVideoId);
  }, [selectedVideoId, processSteps?.burn?.status, loadBaseBurnPreview, loadPublicationSessions]);

  useEffect(() => {
    if (!selectedPublishJob) return;
    if (selectedPublishJob.zip_url) {
      setPublishZipUrl(resolveMediaSrc(selectedPublishJob.zip_url));
    }
    const status = String(selectedPublishJob.status || '').toLowerCase();
    if (status === 'failed') {
      setPublishStatus(
        selectedPublishJob.error
          ? `${t('publish_status_failed')}: ${selectedPublishJob.error}`
          : t('publish_status_failed'),
      );
      setPublishTone('bad');
      return;
    }
    if (status === 'done' || status === 'completed') {
      setPublishStatus(t('publish_status_published'));
      setPublishTone('good');
      return;
    }
    if (status === 'running') {
      setPublishStatus(selectedPublishJob.detail || t('publish_process_running'));
      setPublishTone('neutral');
      return;
    }
    if (status === 'queued') {
      setPublishStatus(
        selectedPublishJob.detail
          ? `${t('publish_status_queued')} ${selectedPublishJob.detail}`
          : t('publish_status_queued'),
      );
      setPublishTone('good');
    }
  }, [resolveMediaSrc, selectedPublishJob, t]);

  const startProcess = async (): Promise<{ ok: boolean; message?: string }> => {
    if (!selectedVideoId || processRunning) return { ok: false };
    setProcessRunning(true);
    setProcessStatus(t('publish_process_starting'));
    setProcessTone('neutral');
    try {
      const committedBurnLayout = await commitSubtitleBurnLayoutSettings();
      const logoPayload = await fetchLogoSettings();
      const autoCorrectPromptText = autoCorrectActive ? autoCorrectPrompt.trim() : '';
      const metadataPromptText = metadataCorrectionPrompt.trim();
      const processedOutputRequired = burnSubtitles || portraitBlurFill || Boolean(logoPayload?.enabled && logoPayload?.logoPath);
      const steps = burnSubtitles
        ? ['keyframes', 'caption', 'transcribe', 'translate', 'burn', 'metadata_zh', 'metadata_en', 'cover']
        : processedOutputRequired
          ? ['keyframes', 'caption', 'transcribe', 'burn', 'metadata_zh', 'metadata_en', 'cover']
          : ['keyframes', 'caption', 'transcribe', 'metadata_zh', 'metadata_en', 'cover'];
      if (autoCorrectPromptText) {
        steps.splice(3, 0, 'polish');
      }
      const resp = await fetch(`${API_URL}/api/videos/${selectedVideoId}/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          async: true,
          steps,
          translationLanguages,
          usePolishedSubtitles: autoCorrectPromptText ? true : usePolishedSubtitles,
          autoCorrectSubtitles: Boolean(autoCorrectPromptText),
          autoCorrectPrompt: autoCorrectPromptText,
          polish_notes: autoCorrectPromptText,
          useCorrectionPromptForMetadata,
          metadataPrompt: metadataPromptText,
          notes: metadataPromptText,
          subtitleLiftRatio: committedBurnLayout.liftRatio,
          subtitleRows: committedBurnLayout.rows,
          subtitleFontScale: committedBurnLayout.fontScale,
          subtitleFontBold: committedBurnLayout.fontBold,
          subtitleFontColor: committedBurnLayout.fontColor,
          subtitleOutlineBold: committedBurnLayout.outlineBold,
          subtitleOutlineColor: committedBurnLayout.outlineColor,
          portraitBlurFill: committedBurnLayout.portraitBlurFill,
          burnLayout: committedBurnLayout,
          publicationMode: publishAsNewSession ? 'new' : 'override',
          publicationSessionId: publishAsNewSession ? null : publicationSessionId,
          ...(logoPayload ? { logo: logoPayload } : {}),
        }),
      });
      const json = await resp.json().catch(() => ({}));
      if (!resp.ok) {
        const message = `${t('publish_process_failed')}: ${json.error || resp.statusText}`;
        setProcessStatus(message);
        setProcessTone('bad');
        return { ok: false, message };
      }
      if (json?.publication_session_id) {
        setPublishAsNewSession(false);
        setRunSelectionTouched(true);
        setPublicationSessionId(Number(json.publication_session_id));
        loadPublicationSessions(selectedVideoId, true);
        if (processedOutputRequired) setPreviewSourceKey(`session:${Number(json.publication_session_id)}`);
      } else if (processedOutputRequired) {
        setPreviewSourceKey('base-burn');
      }
      setProcessStatus(t('publish_process_started'));
      setProcessTone('good');
      loadProcessStatus(selectedVideoId, true);
      return { ok: true };
    } catch (err: any) {
      const message = `${t('publish_process_failed')}: ${err?.message || String(err)}`;
      setProcessStatus(message);
      setProcessTone('bad');
      return { ok: false, message };
    } finally {
      setProcessRunning(false);
    }
  };

  const extractCover = useCallback(
    () => (
      selectedVideoId
        ? requestCoverExtraction(selectedVideoId, selectedCoverSessionId, false)
        : Promise.resolve(false)
    ),
    [requestCoverExtraction, selectedCoverSessionId, selectedVideoId],
  );

  const waitForProcessReady = useCallback(async (videoId: number) => {
    const start = Date.now();
    const intervalMs = 5000;
    while (Date.now() - start < PROCESS_READY_TIMEOUT_MS) {
      const json = await loadProcessStatus(videoId, true);
      if (json?.ready_for_publish) return true;
      const { activeLabel, errorDetail } = summarizeProcessState(json?.steps || null);
      if (errorDetail) {
        throw new Error(errorDetail);
      }
      setPublishStatus(
        activeLabel
          ? t('publish_process_running_step', { value: activeLabel })
          : t('publish_process_running'),
      );
      setPublishTone('neutral');
      await new Promise((resolve) => setTimeout(resolve, intervalMs));
    }
    const finalJson = await loadProcessStatus(videoId, true);
    if (finalJson?.ready_for_publish) return true;
    const { activeLabel, errorDetail } = summarizeProcessState(finalJson?.steps || null);
    if (errorDetail) {
      throw new Error(errorDetail);
    }
    setPublishStatus(
      activeLabel
        ? t('publish_process_running_step', { value: activeLabel })
        : t('publish_process_running'),
    );
    setPublishTone('neutral');
    return false;
  }, [loadProcessStatus, summarizeProcessState, t]);

  const publishNow = async () => {
    if (!selectedVideoId || publishing) return;
    setPublishing(true);
    setPublishStatus(t('publish_status_queued'));
    setPublishTone('neutral');
    try {
      const committedBurnLayout = await commitSubtitleBurnLayoutSettings();
      const autoCorrectPromptText = autoCorrectActive ? autoCorrectPrompt.trim() : '';
      const metadataPromptText = metadataCorrectionPrompt.trim();
      const resp = await fetch(`${API_URL}/api/videos/${selectedVideoId}/publish`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          platforms: selected,
          options: {
            burnSubtitles,
            translationLanguages,
            usePolishedSubtitles: autoCorrectPromptText ? true : usePolishedSubtitles,
            autoCorrectSubtitles: Boolean(autoCorrectPromptText),
            autoCorrectPrompt: autoCorrectPromptText,
            useCorrectionPromptForMetadata,
            metadataPrompt: metadataPromptText,
            subtitleLiftRatio: committedBurnLayout.liftRatio,
            subtitleRows: committedBurnLayout.rows,
            subtitleFontScale: committedBurnLayout.fontScale,
            subtitleFontBold: committedBurnLayout.fontBold,
            subtitleFontColor: committedBurnLayout.fontColor,
            subtitleOutlineBold: committedBurnLayout.outlineBold,
            subtitleOutlineColor: committedBurnLayout.outlineColor,
            portraitBlurFill: committedBurnLayout.portraitBlurFill,
            burnLayout: committedBurnLayout,
            publicationMode: publishAsNewSession ? 'new' : 'override',
            publicationSessionId: publishAsNewSession ? null : publicationSessionId,
          },
        }),
      });
      const json = await resp.json().catch(() => ({}));
      if (!resp.ok) {
        setPublishStatus(`${t('publish_status_failed')}: ${json.error || resp.statusText}`);
        setPublishTone('bad');
        return;
      }
      const queuedJob = json?.job as PublishJob | undefined;
      const zipUrl = queuedJob?.zip_url || json?.zip_url;
      if (zipUrl) {
        setPublishZipUrl(resolveMediaSrc(zipUrl));
      }
      if (json?.publication_session_id) {
        setPublishAsNewSession(false);
        setRunSelectionTouched(true);
        setPublicationSessionId(Number(json.publication_session_id));
        loadPublicationSessions(selectedVideoId, true);
        if (burnSubtitles || portraitBlurFill) setPreviewSourceKey(`session:${Number(json.publication_session_id)}`);
      } else if (burnSubtitles || portraitBlurFill) {
        setPreviewSourceKey('base-burn');
      }
      setPublishStatus(
        json?.detail
          ? `${t('publish_status_queued')} ${json.detail}`
          : t('publish_status_queued'),
      );
      setPublishTone('good');
      loadPublishQueue(true);
    } catch (err: any) {
      setPublishStatus(`${t('publish_status_failed')}: ${err?.message || String(err)}`);
      setPublishTone('bad');
    } finally {
      setPublishing(false);
    }
  };

  const packageMusic = async (post: boolean) => {
    if (musicPackaging) return;
    const audio = musicAudioPath.trim();
    const title = musicTitle.trim();
    if (!audio || !title) {
      setMusicStatus(t('publish_music_required'));
      setMusicTone('bad');
      return;
    }
    const platforms = {
      shipinhao_music: Boolean(musicSelected.shipinhao_music),
      youtube_music: Boolean(musicSelected.youtube_music),
    };
    if (post && !platforms.shipinhao_music && !platforms.youtube_music) {
      setMusicStatus(t('publish_music_platform_required'));
      setMusicTone('bad');
      return;
    }
    setMusicPackaging(true);
    setMusicStatus(post ? t('publish_music_publishing') : t('publish_music_packaging'));
    setMusicTone('neutral');
    try {
      const resp = await fetch(`${API_URL}/api/music/package`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          audio,
          title,
          author: musicAuthor.trim() || 'Musia 慕莎',
          artist: musicArtist.trim() || musicAuthor.trim() || 'Musia 慕莎',
          language: musicLanguage.trim() || '中文',
          genre: musicGenre.trim(),
          lyrics: musicLyricsText,
          lyrics_file: musicLyricsPath.trim(),
          lyrics_json: musicLyricsJsonPath.trim(),
          story: musicStory,
          description: musicDescription,
          cover: splitPathLines(musicCoverPaths),
          cover_video: musicCoverVideoPath.trim(),
          cover_count: Number(musicCoverCount) || 9,
          cover_model: musicCoverModel.trim(),
          aginti_cover_count: Number(musicAgintiCoverCount) || 0,
          codex_cover_count: Number(musicCodexCoverCount) || 0,
          proof: splitPathLines(musicProofPaths),
          website_screenshot: musicWebsiteScreenshot.trim(),
          webapp_screenshot: musicWebappScreenshot.trim(),
          source_url: musicSourceUrl.trim(),
          slug: musicOutputSlug.trim(),
          platforms,
          post,
        }),
      });
      const json = await resp.json().catch(() => ({}));
      if (!resp.ok) {
        throw new Error(json?.error || resp.statusText);
      }
      if (json?.zip_url) {
        setMusicZipUrl(resolveMediaSrc(json.zip_url));
      }
      setMusicStatus(post ? t('publish_music_queued') : t('publish_music_ready'));
      setMusicTone('good');
      await loadPublishQueue(true);
    } catch (err: any) {
      setMusicStatus(`${t('publish_status_failed')}: ${err?.message || String(err)}`);
      setMusicTone('bad');
    } finally {
      setMusicPackaging(false);
    }
  };

  const renderRunSelector = (
    menuOpen: boolean,
    setMenuOpen: React.Dispatch<React.SetStateAction<boolean>>,
    hint: string,
  ) => (
    <View style={styles.runSelectorBlock}>
      <Text style={styles.optionLabel}>{t('publish_run_title')}</Text>
      <Text style={styles.optionHint}>{hint}</Text>
      <Pressable
        style={[styles.runSelectorButton, !selectedVideo && styles.btnDisabled]}
        onPress={() => setMenuOpen((prev) => !prev)}
        disabled={!selectedVideo}
      >
        <View style={styles.runSelectorText}>
          <Text style={styles.runSelectorLabel} numberOfLines={1}>
            {selectedRunOption?.label || t('publish_run_current')}
          </Text>
          <Text style={styles.runSelectorHint} numberOfLines={1}>
            {selectedRunOption?.hint || t('publish_run_current_hint')}
          </Text>
        </View>
        <FontAwesome name={menuOpen ? 'chevron-up' : 'chevron-down'} size={13} color="#334155" />
      </Pressable>
      {menuOpen ? (
        <View style={styles.runDropdown}>
          {sessionLoading ? <ActivityIndicator style={{ marginVertical: 8 }} /> : null}
          <ScrollView style={styles.runDropdownScroll} nestedScrollEnabled>
            {publicationRunOptions.map((option) => {
              const active = option.key === selectedRunKey;
              return (
                <View key={option.key} style={[styles.runOptionRow, active && styles.runOptionRowActive]}>
                  <Pressable
                    style={styles.runOptionMain}
                    onPress={() => selectPublicationRun(option.key)}
                  >
                    <Text style={[styles.runOptionLabel, active && styles.runOptionLabelActive]} numberOfLines={1}>
                      {option.label}
                    </Text>
                    <Text style={styles.runOptionHint} numberOfLines={1}>
                      {option.hint}
                    </Text>
                  </Pressable>
                  {option.session ? (
                    <Pressable
                      style={styles.sessionDelete}
                      onPress={(event: any) => {
                        event?.stopPropagation?.();
                        deletePublicationSession(option.session!.id);
                      }}
                    >
                      <FontAwesome name="trash" size={13} color="#b91c1c" />
                    </Pressable>
                  ) : null}
                </View>
              );
            })}
          </ScrollView>
        </View>
      ) : null}
    </View>
  );

  const renderSubtitleSourceSelector = () => (
    <View style={styles.runSelectorBlock}>
      <Text style={styles.optionLabel}>{t('publish_option_subtitle_source_title')}</Text>
      <Text style={styles.optionHint}>{t('publish_option_subtitle_source_hint')}</Text>
      <Pressable
        style={[styles.runSelectorButton, !publishOptionsLoaded && styles.btnDisabled]}
        onPress={() => setSubtitleSourceMenuOpen((prev) => !prev)}
        disabled={!publishOptionsLoaded}
      >
        <View style={styles.runSelectorText}>
          <Text style={styles.runSelectorLabel} numberOfLines={1}>
            {selectedSubtitleSource.label}
          </Text>
          <Text style={styles.runSelectorHint} numberOfLines={1}>
            {selectedSubtitleSource.hint}
          </Text>
        </View>
        <FontAwesome name={subtitleSourceMenuOpen ? 'chevron-up' : 'chevron-down'} size={13} color="#334155" />
      </Pressable>
      {subtitleSourceMenuOpen ? (
        <View style={styles.runDropdown}>
          {subtitleSourceOptions.map((option) => {
            const active = option.key === selectedSubtitleSource.key;
            return (
              <Pressable
                key={option.key}
                style={[styles.runOptionRow, active && styles.runOptionRowActive]}
                onPress={() => selectSubtitleSource(option.key)}
              >
                <View style={styles.runOptionMain}>
                  <Text style={[styles.runOptionLabel, active && styles.runOptionLabelActive]} numberOfLines={1}>
                    {option.label}
                  </Text>
                  <Text style={styles.runOptionHint} numberOfLines={1}>
                    {option.hint}
                  </Text>
                </View>
              </Pressable>
            );
          })}
        </View>
      ) : null}
    </View>
  );

  const renderPreviewSourceSelector = () => (
    <View style={styles.previewSourceBlock}>
      <Pressable
        style={[styles.runSelectorButton, !selectedVideo && styles.btnDisabled]}
        onPress={() => setPreviewSourceMenuOpen((prev) => !prev)}
        disabled={!selectedVideo}
      >
        <View style={styles.runSelectorText}>
          <Text style={styles.runSelectorLabel} numberOfLines={1}>
            {selectedPreviewSource?.label || t('publish_preview_original')}
          </Text>
          <Text style={styles.runSelectorHint} numberOfLines={1}>
            {selectedPreviewSource?.hint || t('publish_preview_original_hint')}
          </Text>
        </View>
        <FontAwesome name={previewSourceMenuOpen ? 'chevron-up' : 'chevron-down'} size={13} color="#334155" />
      </Pressable>
      {previewSourceMenuOpen ? (
        <View style={styles.runDropdown}>
          <ScrollView style={styles.runDropdownScroll} nestedScrollEnabled>
            {previewSourceOptions.map((option) => {
              const active = option.key === previewSourceKey;
              return (
                <Pressable
                  key={option.key}
                  style={[styles.runOptionRow, active && styles.runOptionRowActive]}
                  onPress={() => {
                    setPreviewSourceKey(option.key);
                    setPreviewSourceMenuOpen(false);
                  }}
                >
                  <View style={styles.runOptionMain}>
                    <Text style={[styles.runOptionLabel, active && styles.runOptionLabelActive]} numberOfLines={1}>
                      {option.label}
                    </Text>
                    <Text style={styles.runOptionHint} numberOfLines={1}>
                      {option.hint}
                    </Text>
                  </View>
                </Pressable>
              );
            })}
          </ScrollView>
        </View>
      ) : null}
    </View>
  );

  return (
    <ScrollView contentContainerStyle={styles.scrollContent}>
      <View style={styles.container}>
        <Text style={styles.title}>{t('publish_title')}</Text>
        <Text style={styles.sub}>{t('publish_subtitle')}</Text>
        <View style={styles.modeToggleRow}>
          <Pressable
            style={[styles.modeToggleButton, publishMode === 'video' && styles.modeToggleButtonActive]}
            onPress={() => setPublishMode('video')}
          >
            <FontAwesome name="video-camera" size={13} color={publishMode === 'video' ? 'white' : '#0f172a'} />
            <Text style={[styles.modeToggleText, publishMode === 'video' && styles.modeToggleTextActive]}>
              {t('publish_mode_video')}
            </Text>
          </Pressable>
          <Pressable
            style={[styles.modeToggleButton, publishMode === 'music' && styles.modeToggleButtonActive]}
            onPress={() => setPublishMode('music')}
          >
            <FontAwesome name="music" size={13} color={publishMode === 'music' ? 'white' : '#0f172a'} />
            <Text style={[styles.modeToggleText, publishMode === 'music' && styles.modeToggleTextActive]}>
              {t('publish_mode_music')}
            </Text>
          </Pressable>
        </View>

        {publishMode === 'music' ? (
          <View style={styles.card}>
            <Text style={styles.sectionTitle}>{t('publish_music_title')}</Text>
            <Text style={styles.sectionHint}>{t('publish_music_hint')}</Text>
            <View style={styles.platformGrid}>
              {MUSIC_PLATFORMS.map((platform) => {
                const isActive = musicSelected[platform.key];
                return (
                  <Pressable
                    key={platform.key}
                    style={[styles.platformChip, isActive && styles.platformChipActive]}
                    onPress={() =>
                      setMusicSelected((prev) => ({ ...prev, [platform.key]: !prev[platform.key] }))
                    }
                  >
                    <Text style={[styles.platformText, isActive && styles.platformTextActive]}>
                      {platform.label}
                    </Text>
                  </Pressable>
                );
              })}
            </View>
            <Text style={styles.selectedText}>
              {t('label_selected', {
                value: selectedMusicList.length ? selectedMusicList.join(', ') : t('label_none'),
              })}
            </Text>
            <View style={styles.musicFieldGrid}>
              <View style={styles.musicFieldWide}>
                <Text style={styles.optionLabel}>{t('publish_music_audio')}</Text>
                <TextInput value={musicAudioPath} onChangeText={setMusicAudioPath} style={styles.fieldInput} placeholder="/path/song.mp3" />
              </View>
              <View style={styles.musicFieldWide}>
                <Text style={styles.optionLabel}>{t('publish_music_song_title')}</Text>
                <TextInput value={musicTitle} onChangeText={setMusicTitle} style={styles.fieldInput} placeholder="Song title" />
              </View>
              <View style={styles.musicField}>
                <Text style={styles.optionLabel}>{t('publish_music_author')}</Text>
                <TextInput value={musicAuthor} onChangeText={setMusicAuthor} style={styles.fieldInput} />
              </View>
              <View style={styles.musicField}>
                <Text style={styles.optionLabel}>{t('publish_music_artist')}</Text>
                <TextInput value={musicArtist} onChangeText={setMusicArtist} style={styles.fieldInput} />
              </View>
              <View style={styles.musicField}>
                <Text style={styles.optionLabel}>{t('publish_music_language')}</Text>
                <TextInput value={musicLanguage} onChangeText={setMusicLanguage} style={styles.fieldInput} />
              </View>
              <View style={styles.musicField}>
                <Text style={styles.optionLabel}>{t('publish_music_genre')}</Text>
                <TextInput value={musicGenre} onChangeText={setMusicGenre} style={styles.fieldInput} />
              </View>
              <View style={styles.musicFieldWide}>
                <Text style={styles.optionLabel}>{t('publish_music_lyrics')}</Text>
                <TextInput value={musicLyricsText} onChangeText={setMusicLyricsText} multiline style={styles.fieldInputMultiline} />
              </View>
              <View style={styles.musicField}>
                <Text style={styles.optionLabel}>{t('publish_music_lyrics_file')}</Text>
                <TextInput value={musicLyricsPath} onChangeText={setMusicLyricsPath} style={styles.fieldInput} placeholder="/path/lyrics.txt" />
              </View>
              <View style={styles.musicField}>
                <Text style={styles.optionLabel}>{t('publish_music_lyrics_json')}</Text>
                <TextInput value={musicLyricsJsonPath} onChangeText={setMusicLyricsJsonPath} style={styles.fieldInput} placeholder="/path/lyrics.json" />
              </View>
              <View style={styles.musicFieldWide}>
                <Text style={styles.optionLabel}>{t('publish_music_story')}</Text>
                <TextInput value={musicStory} onChangeText={setMusicStory} multiline style={styles.fieldInputMultiline} />
              </View>
              <View style={styles.musicFieldWide}>
                <Text style={styles.optionLabel}>{t('publish_music_description')}</Text>
                <TextInput value={musicDescription} onChangeText={setMusicDescription} multiline style={styles.fieldInputMultiline} />
              </View>
              <View style={styles.musicFieldWide}>
                <Text style={styles.optionLabel}>{t('publish_music_covers')}</Text>
                <TextInput
                  value={musicCoverPaths}
                  onChangeText={setMusicCoverPaths}
                  multiline
                  style={styles.fieldInputMultiline}
                  placeholder={'/path/cover1.png\n/path/cover2.png'}
                />
              </View>
              <View style={styles.musicFieldWide}>
                <Text style={styles.optionLabel}>{t('publish_music_cover_video')}</Text>
                <TextInput value={musicCoverVideoPath} onChangeText={setMusicCoverVideoPath} style={styles.fieldInput} placeholder="/path/reference-video.mp4" />
              </View>
              <View style={styles.musicField}>
                <Text style={styles.optionLabel}>{t('publish_music_cover_count')}</Text>
                <TextInput value={musicCoverCount} onChangeText={setMusicCoverCount} keyboardType="number-pad" style={styles.fieldInput} />
              </View>
              <View style={styles.musicField}>
                <Text style={styles.optionLabel}>{t('publish_music_cover_model')}</Text>
                <TextInput value={musicCoverModel} onChangeText={setMusicCoverModel} style={styles.fieldInput} />
              </View>
              <View style={styles.musicField}>
                <Text style={styles.optionLabel}>{t('publish_music_aginti_count')}</Text>
                <TextInput value={musicAgintiCoverCount} onChangeText={setMusicAgintiCoverCount} keyboardType="number-pad" style={styles.fieldInput} />
              </View>
              <View style={styles.musicField}>
                <Text style={styles.optionLabel}>{t('publish_music_codex_count')}</Text>
                <TextInput value={musicCodexCoverCount} onChangeText={setMusicCodexCoverCount} keyboardType="number-pad" style={styles.fieldInput} />
              </View>
              <View style={styles.musicFieldWide}>
                <Text style={styles.optionLabel}>{t('publish_music_proofs')}</Text>
                <TextInput value={musicProofPaths} onChangeText={setMusicProofPaths} multiline style={styles.fieldInputMultiline} placeholder="/path/proof-or-screenshot.png" />
              </View>
              <View style={styles.musicField}>
                <Text style={styles.optionLabel}>{t('publish_music_website_screenshot')}</Text>
                <TextInput value={musicWebsiteScreenshot} onChangeText={setMusicWebsiteScreenshot} style={styles.fieldInput} />
              </View>
              <View style={styles.musicField}>
                <Text style={styles.optionLabel}>{t('publish_music_webapp_screenshot')}</Text>
                <TextInput value={musicWebappScreenshot} onChangeText={setMusicWebappScreenshot} style={styles.fieldInput} />
              </View>
              <View style={styles.musicField}>
                <Text style={styles.optionLabel}>{t('publish_music_source_url')}</Text>
                <TextInput value={musicSourceUrl} onChangeText={setMusicSourceUrl} style={styles.fieldInput} />
              </View>
              <View style={styles.musicField}>
                <Text style={styles.optionLabel}>{t('publish_music_slug')}</Text>
                <TextInput value={musicOutputSlug} onChangeText={setMusicOutputSlug} style={styles.fieldInput} />
              </View>
            </View>
            <View style={styles.musicActions}>
              <Pressable
                style={[styles.secondaryButton, musicPackaging && styles.btnDisabled]}
                onPress={() => void packageMusic(false)}
                disabled={musicPackaging}
              >
                <Text style={styles.secondaryButtonText}>{t('publish_music_prepare')}</Text>
              </Pressable>
              <Pressable
                style={[styles.publishButton, musicPackaging && styles.btnDisabled]}
                onPress={() => void packageMusic(true)}
                disabled={musicPackaging}
              >
                <View style={styles.btnContent}>
                  {musicPackaging && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
                  <Text style={styles.publishButtonText}>{t('publish_music_publish')}</Text>
                </View>
              </Pressable>
            </View>
            {musicStatus ? <Text style={[styles.status, toneStyle(musicTone)]}>{musicStatus}</Text> : null}
            {musicZipUrl ? <Text style={styles.zipText}>{t('publish_zip_ready', { value: musicZipUrl })}</Text> : null}
          </View>
        ) : null}

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>{t('publish_video_select_title')}</Text>
          <Text style={styles.sectionHint}>{t('publish_video_select_hint')}</Text>
          {loadingVideos ? (
            <ActivityIndicator style={{ marginTop: 12 }} />
          ) : videos.length ? (
            <FlatList
              data={visibleVideos}
              keyExtractor={(video) => String(video.id)}
              style={styles.videoListScroll}
              contentContainerStyle={styles.videoList}
              onViewableItemsChanged={onViewableItemsChanged}
              viewabilityConfig={viewabilityConfigRef.current}
              onEndReached={() => {
                if (hasMoreVideos) loadMoreVideos();
              }}
              onEndReachedThreshold={0.4}
              onLayout={(event) => setListHeight(event.nativeEvent.layout.height)}
              onContentSizeChange={(_width, height) => setListContentHeight(height)}
              nestedScrollEnabled
              renderItem={({ item: video }) => {
                const previewUrl = video.preview_media_url || video.media_url;
                const mediaSrc = resolveMediaSrc(previewUrl);
                const imageSrc = resolveMediaSrc(video.preview_image_url || null);
                const isActive = selectedVideoId === video.id;
                const title = video.title || t('library_video_fallback', { id: video.id });
                return (
                  <Pressable
                    key={video.id}
                    style={[styles.videoRow, isActive && styles.videoRowActive]}
                    onPress={() => setSelectedVideoId(video.id)}
                  >
                    <View style={styles.videoPreview}>
                      {imageSrc ? (
                        <Image source={{ uri: imageSrc }} style={styles.processPreviewImage} />
                      ) : Platform.OS === 'web' && mediaSrc ? (
                        React.createElement('video', {
                          src: mediaSrc,
                          style: { width: '100%', height: '100%', borderRadius: 10, objectFit: 'cover' },
                          muted: true,
                          playsInline: true,
                          preload: 'metadata',
                        })
                      ) : (
                        <Text style={styles.previewLabel}>{t('library_preview')}</Text>
                      )}
                    </View>
                    <View style={styles.videoMeta}>
                      <Text style={styles.videoTitle} numberOfLines={1}>
                        {title}
                      </Text>
                      <Text style={styles.videoPath} numberOfLines={1}>
                        {video.file_path}
                      </Text>
                      <Text style={styles.videoTime}>
                        {video.created_at?.slice(0, 19).replace('T', ' ')}
                      </Text>
                    </View>
                    <View style={styles.videoActions}>
                      <View style={[styles.selectBadge, isActive && styles.selectBadgeActive]}>
                        {isActive ? <FontAwesome name="check" size={12} color="white" /> : null}
                      </View>
                      <Pressable
                        style={styles.videoDeleteButton}
                        onPress={(event) => {
                          event.stopPropagation?.();
                          setDeleteVideoError('');
                          setConfirmDeleteVideo(video);
                        }}
                      >
                        <FontAwesome name="trash" size={13} color="#b91c1c" />
                      </Pressable>
                    </View>
                  </Pressable>
                );
              }}
              ListFooterComponent={
                hasMoreVideos ? (
                  <Pressable style={styles.moreButton} onPress={loadMoreVideos}>
                    <Text style={styles.moreButtonText}>{t('list_more')}</Text>
                  </Pressable>
                ) : (
                  <View style={styles.footerSpacer} />
                )
              }
            />
          ) : (
            <Text style={styles.empty}>{t('publish_video_empty')}</Text>
          )}
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>{t('publish_select_title')}</Text>
          <Text style={styles.sectionHint}>{t('publish_select_hint')}</Text>

          <View style={styles.platformGrid}>
            {PLATFORMS.map((platform) => {
              const isActive = selected[platform.key];
              return (
                <Pressable
                  key={platform.key}
                  style={[styles.platformChip, isActive && styles.platformChipActive]}
                  onPress={() =>
                    setSelected((prev) => ({ ...prev, [platform.key]: !prev[platform.key] }))
                  }
                >
                  <Text style={[styles.platformText, isActive && styles.platformTextActive]}>
                    {platform.label}
                  </Text>
                </Pressable>
              );
            })}
          </View>

          <Text style={styles.selectedText}>
            {t('label_selected', {
              value: selectedList.length ? selectedList.join(', ') : t('label_none'),
            })}
          </Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>{t('publish_process_title')}</Text>
          <Text style={styles.sectionHint}>{t('publish_process_hint')}</Text>
          <View style={styles.publishOptionRow}>
            <View style={styles.publishOptionText}>
              <Text style={styles.optionLabel}>{t('publish_option_burn_title')}</Text>
              <Text style={styles.optionHint}>
                {burnSubtitles ? t('publish_option_burn_on') : t('publish_option_burn_off')}
              </Text>
            </View>
            <Switch
              value={burnSubtitles}
              onValueChange={updateBurnSubtitles}
              disabled={!publishOptionsLoaded}
              trackColor={{ false: '#e2e8f0', true: '#2563eb' }}
              thumbColor={burnSubtitles ? '#f8fafc' : '#f1f5f9'}
            />
          </View>
          <View style={styles.languageOptionRow}>
            <Text style={styles.optionLabel}>{t('publish_option_language_count_title')}</Text>
            <View style={styles.languageChipGroup}>
              {AVAILABLE_TRANSLATION_LANGUAGES.map((language) => {
                const active = translationLanguages.includes(language);
                const activeIndex = translationLanguages.indexOf(language);
                const effectiveRows = Math.max(subtitleRows, translationLanguages.length);
                const targetSlot = active && activeIndex >= 0 ? Math.max(1, effectiveRows - activeIndex) : null;
                const shortLabel = LANGUAGE_SHORT_LABELS[language] || language.toUpperCase();
                return (
                  <Pressable
                    key={language}
                    accessibilityLabel={LANGUAGE_LABELS[language] || language}
                    style={[styles.languageChip, active && styles.languageChipActive]}
                    onPress={() => toggleTranslationLanguage(language)}
                    disabled={!publishOptionsLoaded}
                  >
                    <Text style={[styles.languageChipText, active && styles.languageChipTextActive]}>
                      {targetSlot ? `${targetSlot} ${shortLabel}` : shortLabel}
                    </Text>
                  </Pressable>
                );
              })}
            </View>
          </View>
          <View style={styles.liftRatioRow}>
            <View style={styles.publishOptionText}>
              <Text style={styles.optionLabel}>{t('publish_option_lift_ratio_title')}</Text>
              <Text style={styles.optionHint}>
                {t('publish_option_lift_ratio_hint', { value: formatSubtitleLiftRatio(subtitleLiftRatio) })}
              </Text>
            </View>
            <View style={styles.liftRatioControls}>
              <Pressable
                style={[styles.liftRatioButton, !publishOptionsLoaded && styles.btnDisabled]}
                onPress={() => setAndPersistSubtitleLiftRatio(0)}
                disabled={!publishOptionsLoaded}
              >
                <Text style={styles.liftRatioButtonText}>0</Text>
              </Pressable>
              <Pressable
                style={[styles.liftRatioButton, !publishOptionsLoaded && styles.btnDisabled]}
                onPress={() => adjustSubtitleLiftRatio(-0.01)}
                disabled={!publishOptionsLoaded}
              >
                <Text style={styles.liftRatioButtonText}>-</Text>
              </Pressable>
              <TextInput
                value={subtitleLiftInput}
                onChangeText={setSubtitleLiftInput}
                onBlur={() => void commitSubtitleLiftRatio()}
                onSubmitEditing={() => void commitSubtitleLiftRatio()}
                keyboardType="decimal-pad"
                placeholder="0.1"
                editable={publishOptionsLoaded}
                style={[styles.liftRatioInput, !publishOptionsLoaded && styles.liftRatioInputDisabled]}
              />
              <Pressable
                style={[styles.liftRatioButton, !publishOptionsLoaded && styles.btnDisabled]}
                onPress={() => adjustSubtitleLiftRatio(0.01)}
                disabled={!publishOptionsLoaded}
              >
                <Text style={styles.liftRatioButtonText}>+</Text>
              </Pressable>
            </View>
          </View>
          <View style={styles.liftRatioRow}>
            <View style={styles.publishOptionText}>
              <Text style={styles.optionLabel}>{t('publish_option_rows_title')}</Text>
              <Text style={styles.optionHint}>
                {t('publish_option_rows_hint', { value: subtitleRows })}
              </Text>
            </View>
            <View style={styles.liftRatioControls}>
              <Pressable
                style={[styles.liftRatioButton, !publishOptionsLoaded && styles.btnDisabled]}
                onPress={() => setAndPersistSubtitleRows(DEFAULT_SUBTITLE_ROWS)}
                disabled={!publishOptionsLoaded}
              >
                <Text style={styles.liftRatioButtonText}>4</Text>
              </Pressable>
              <Pressable
                style={[styles.liftRatioButton, !publishOptionsLoaded && styles.btnDisabled]}
                onPress={() => adjustSubtitleRows(-1)}
                disabled={!publishOptionsLoaded}
              >
                <Text style={styles.liftRatioButtonText}>-</Text>
              </Pressable>
              <TextInput
                value={subtitleRowsInput}
                onChangeText={setSubtitleRowsInput}
                onBlur={() => void commitSubtitleRows()}
                onSubmitEditing={() => void commitSubtitleRows()}
                keyboardType="number-pad"
                placeholder="4"
                editable={publishOptionsLoaded}
                style={[styles.liftRatioInput, !publishOptionsLoaded && styles.liftRatioInputDisabled]}
              />
              <Pressable
                style={[styles.liftRatioButton, !publishOptionsLoaded && styles.btnDisabled]}
                onPress={() => adjustSubtitleRows(1)}
                disabled={!publishOptionsLoaded}
              >
                <Text style={styles.liftRatioButtonText}>+</Text>
              </Pressable>
            </View>
          </View>
          <View style={styles.liftRatioRow}>
            <View style={styles.publishOptionText}>
              <Text style={styles.optionLabel}>{t('publish_option_font_size_title')}</Text>
              <Text style={styles.optionHint}>
                {t('publish_option_font_size_hint', { value: formatSubtitleFontScale(subtitleFontScale) })}
              </Text>
            </View>
            <View style={styles.liftRatioControls}>
              <Pressable
                style={[styles.liftRatioButton, !publishOptionsLoaded && styles.btnDisabled]}
                onPress={() => setAndPersistSubtitleFontScale(DEFAULT_SUBTITLE_FONT_SCALE)}
                disabled={!publishOptionsLoaded}
              >
                <Text style={styles.liftRatioButtonText}>1</Text>
              </Pressable>
              <Pressable
                style={[styles.liftRatioButton, !publishOptionsLoaded && styles.btnDisabled]}
                onPress={() => adjustSubtitleFontScale(-0.05)}
                disabled={!publishOptionsLoaded}
              >
                <Text style={styles.liftRatioButtonText}>-</Text>
              </Pressable>
              <TextInput
                value={subtitleFontScaleInput}
                onChangeText={setSubtitleFontScaleInput}
                onBlur={() => void commitSubtitleFontScale()}
                onSubmitEditing={() => void commitSubtitleFontScale()}
                keyboardType="decimal-pad"
                placeholder="1"
                editable={publishOptionsLoaded}
                style={[styles.liftRatioInput, !publishOptionsLoaded && styles.liftRatioInputDisabled]}
              />
              <Pressable
                style={[styles.liftRatioButton, !publishOptionsLoaded && styles.btnDisabled]}
                onPress={() => adjustSubtitleFontScale(0.05)}
                disabled={!publishOptionsLoaded}
              >
                <Text style={styles.liftRatioButtonText}>+</Text>
              </Pressable>
            </View>
          </View>
          <View style={styles.subtitleStyleRow}>
            <View style={styles.subtitleStyleSwitch}>
              <View style={styles.publishOptionText}>
                <Text style={styles.optionLabel}>{t('publish_option_font_bold_title')}</Text>
                <Text style={styles.optionHint}>
                  {subtitleFontBold ? t('publish_option_font_bold_on') : t('publish_option_font_bold_off')}
                </Text>
              </View>
              <Switch
                value={subtitleFontBold}
                onValueChange={updateSubtitleFontBold}
                disabled={!publishOptionsLoaded}
                trackColor={{ false: '#e2e8f0', true: '#2563eb' }}
                thumbColor={subtitleFontBold ? '#f8fafc' : '#f1f5f9'}
              />
            </View>
            <View style={styles.subtitleStyleSwitch}>
              <View style={styles.publishOptionText}>
                <Text style={styles.optionLabel}>{t('publish_option_outline_bold_title')}</Text>
                <Text style={styles.optionHint}>
                  {subtitleOutlineBold ? t('publish_option_outline_bold_on') : t('publish_option_outline_bold_off')}
                </Text>
              </View>
              <Switch
                value={subtitleOutlineBold}
                onValueChange={updateSubtitleOutlineBold}
                disabled={!publishOptionsLoaded}
                trackColor={{ false: '#e2e8f0', true: '#2563eb' }}
                thumbColor={subtitleOutlineBold ? '#f8fafc' : '#f1f5f9'}
              />
            </View>
          </View>
          <View style={styles.subtitleColorRow}>
            <View style={styles.subtitleColorField}>
              <Text style={styles.optionLabel}>{t('publish_option_font_color_title')}</Text>
              <View style={styles.colorControl}>
                <View style={[styles.colorSwatch, { backgroundColor: normalizeHexColor(subtitleFontColor, DEFAULT_SUBTITLE_FONT_COLOR) }]} />
                <TextInput
                  value={subtitleFontColor}
                  onChangeText={setSubtitleFontColor}
                  onBlur={() => void commitSubtitleFontColor()}
                  onSubmitEditing={() => void commitSubtitleFontColor()}
                  placeholder="#FFFFFF"
                  autoCapitalize="characters"
                  editable={publishOptionsLoaded}
                  style={[styles.colorInput, !publishOptionsLoaded && styles.liftRatioInputDisabled]}
                />
              </View>
            </View>
            <View style={styles.subtitleColorField}>
              <Text style={styles.optionLabel}>{t('publish_option_outline_color_title')}</Text>
              <View style={styles.colorControl}>
                <View style={[styles.colorSwatch, { backgroundColor: normalizeHexColor(subtitleOutlineColor, DEFAULT_SUBTITLE_OUTLINE_COLOR) }]} />
                <TextInput
                  value={subtitleOutlineColor}
                  onChangeText={setSubtitleOutlineColor}
                  onBlur={() => void commitSubtitleOutlineColor()}
                  onSubmitEditing={() => void commitSubtitleOutlineColor()}
                  placeholder="#000000"
                  autoCapitalize="characters"
                  editable={publishOptionsLoaded}
                  style={[styles.colorInput, !publishOptionsLoaded && styles.liftRatioInputDisabled]}
                />
              </View>
            </View>
          </View>
          <View style={styles.publishOptionRow}>
            <View style={styles.publishOptionText}>
              <Text style={styles.optionLabel}>{t('publish_option_portrait_title')}</Text>
              <Text style={styles.optionHint}>
                {portraitBlurFill ? t('publish_option_portrait_on') : t('publish_option_portrait_off')}
              </Text>
            </View>
            <Switch
              value={portraitBlurFill}
              onValueChange={updatePortraitBlurFill}
              disabled={!publishOptionsLoaded}
              trackColor={{ false: '#e2e8f0', true: '#2563eb' }}
              thumbColor={portraitBlurFill ? '#f8fafc' : '#f1f5f9'}
            />
          </View>
          {portraitBlurFill ? (
            <View style={styles.liftRatioRow}>
              <View style={styles.publishOptionText}>
                <Text style={styles.optionLabel}>{t('publish_option_portrait_mode_title')}</Text>
                <Text style={styles.optionHint}>
                  {portraitBlurMode === 'center'
                    ? t('publish_option_portrait_mode_center_hint')
                    : portraitBlurMode === 'custom'
                      ? t('publish_option_portrait_mode_custom_hint')
                      : t('publish_option_portrait_mode_lalachan_hint')}
                </Text>
              </View>
              <View style={styles.languageChipGroup}>
                {(['lalachan', 'center', 'custom'] as PortraitBlurMode[]).map((mode) => {
                  const active = portraitBlurMode === mode;
                  return (
                    <Pressable
                      key={mode}
                      style={[styles.languageChip, active && styles.languageChipActive]}
                      onPress={() => updatePortraitBlurMode(mode)}
                      disabled={!publishOptionsLoaded}
                    >
                      <Text style={[styles.languageChipText, active && styles.languageChipTextActive]}>
                        {t(`publish_option_portrait_mode_${mode}`)}
                      </Text>
                    </Pressable>
                  );
                })}
              </View>
            </View>
          ) : null}
          {portraitBlurFill && portraitBlurMode === 'lalachan' ? (
            <View style={styles.liftRatioRow}>
              <View style={styles.publishOptionText}>
                <Text style={styles.optionLabel}>{t('publish_option_portrait_shift_title')}</Text>
                <Text style={styles.optionHint}>
                  {t('publish_option_portrait_shift_hint', {
                    value: formatPortraitBottomSpaceRatio(portraitBottomSpaceRatio),
                  })}
                </Text>
              </View>
              <View style={styles.liftRatioControls}>
                <Pressable
                  style={[styles.liftRatioButton, !publishOptionsLoaded && styles.btnDisabled]}
                  onPress={() => {
                    setPortraitBottomSpaceRatio(DEFAULT_PORTRAIT_BOTTOM_SPACE_RATIO);
                    setPortraitBottomSpaceInput(formatPortraitBottomSpaceRatio(DEFAULT_PORTRAIT_BOTTOM_SPACE_RATIO));
                    void persistBurnLayout({
                      portraitBlurFill: {
                        enabled: portraitBlurFill,
                        mode: portraitBlurMode,
                        foregroundY: portraitForegroundY,
                        bottomSpaceRatio: DEFAULT_PORTRAIT_BOTTOM_SPACE_RATIO,
                      },
                    });
                  }}
                  disabled={!publishOptionsLoaded}
                >
                  <Text style={styles.liftRatioButtonText}>0.4</Text>
                </Pressable>
                <TextInput
                  value={portraitBottomSpaceInput}
                  onChangeText={setPortraitBottomSpaceInput}
                  onBlur={() => void commitPortraitBottomSpaceRatio()}
                  onSubmitEditing={() => void commitPortraitBottomSpaceRatio()}
                  keyboardType="decimal-pad"
                  placeholder="0.4"
                  editable={publishOptionsLoaded}
                  style={[styles.liftRatioInput, !publishOptionsLoaded && styles.liftRatioInputDisabled]}
                />
              </View>
            </View>
          ) : null}
          {portraitBlurFill && portraitBlurMode === 'custom' ? (
            <View style={styles.liftRatioRow}>
              <View style={styles.publishOptionText}>
                <Text style={styles.optionLabel}>{t('publish_option_portrait_y_title')}</Text>
                <Text style={styles.optionHint}>
                  {t('publish_option_portrait_y_hint', { value: String(portraitForegroundY) })}
                </Text>
              </View>
              <View style={styles.liftRatioControls}>
                <Pressable
                  style={[styles.liftRatioButton, !publishOptionsLoaded && styles.btnDisabled]}
                  onPress={() => {
                    setPortraitForegroundY(DEFAULT_PORTRAIT_FOREGROUND_Y);
                    setPortraitForegroundYInput(String(DEFAULT_PORTRAIT_FOREGROUND_Y));
                    void persistBurnLayout({
                      portraitBlurFill: {
                        enabled: portraitBlurFill,
                        mode: portraitBlurMode,
                        foregroundY: DEFAULT_PORTRAIT_FOREGROUND_Y,
                        bottomSpaceRatio: portraitBottomSpaceRatio,
                      },
                    });
                  }}
                  disabled={!publishOptionsLoaded}
                >
                  <Text style={styles.liftRatioButtonText}>240</Text>
                </Pressable>
                <TextInput
                  value={portraitForegroundYInput}
                  onChangeText={setPortraitForegroundYInput}
                  onBlur={() => void commitPortraitForegroundY()}
                  onSubmitEditing={() => void commitPortraitForegroundY()}
                  keyboardType="number-pad"
                  placeholder="240"
                  editable={publishOptionsLoaded}
                  style={[styles.liftRatioInput, !publishOptionsLoaded && styles.liftRatioInputDisabled]}
                />
              </View>
            </View>
          ) : null}
          {portraitBlurFill ? (
            <View style={styles.portraitMetricsCard}>
              <View style={styles.portraitMetricsHeader}>
                <View style={styles.publishOptionText}>
                  <Text style={styles.optionLabel}>{t('publish_portrait_layout_title')}</Text>
                  <Text style={styles.optionHint}>
                    {portraitLayoutMetrics
                      ? t('publish_portrait_layout_source', {
                          width: String(portraitLayoutMetrics.sourceWidth),
                          height: String(portraitLayoutMetrics.sourceHeight),
                        })
                      : t('publish_portrait_layout_waiting')}
                  </Text>
                </View>
                <Pressable
                  style={[styles.miniButton, !portraitLayoutMetrics && styles.btnDisabled]}
                  onPress={() => setPortraitLayoutModalOpen(true)}
                  disabled={!portraitLayoutMetrics}
                >
                  <Text style={styles.miniButtonText}>{t('publish_portrait_layout_view')}</Text>
                </Pressable>
              </View>
              {portraitLayoutMetrics ? (
                <>
                  <View style={styles.portraitMetricRow}>
                    <View style={styles.portraitMetricChip}>
                      <Text style={styles.portraitMetricLabel}>{t('publish_portrait_layout_top')}</Text>
                      <Text style={styles.portraitMetricValue}>
                        {portraitLayoutMetrics.top}px · {formatMetricPercent(portraitLayoutMetrics.top / portraitLayoutMetrics.outputHeight)}
                      </Text>
                    </View>
                    <View style={styles.portraitMetricChip}>
                      <Text style={styles.portraitMetricLabel}>{t('publish_portrait_layout_foreground')}</Text>
                      <Text style={styles.portraitMetricValue}>
                        {portraitLayoutMetrics.foregroundWidth}x{portraitLayoutMetrics.foregroundHeight}
                      </Text>
                    </View>
                    <View style={styles.portraitMetricChip}>
                      <Text style={styles.portraitMetricLabel}>{t('publish_portrait_layout_bottom')}</Text>
                      <Text style={styles.portraitMetricValue}>
                        {portraitLayoutMetrics.bottom}px · {formatMetricPercent(portraitLayoutMetrics.bottom / portraitLayoutMetrics.outputHeight)}
                      </Text>
                    </View>
                  </View>
                  <Text style={styles.optionHint}>
                    {t('publish_portrait_layout_shift', {
                      value: `${portraitLayoutMetrics.centerShift}px`,
                      ratio: formatPortraitBottomSpaceRatio(portraitLayoutMetrics.centerShiftRatio),
                    })}
                    {portraitLayoutMetrics.narrowed ? ` ${t('publish_portrait_layout_narrowed')}` : ''}
                  </Text>
                </>
              ) : (
                <Text style={styles.optionHint}>{t('publish_portrait_layout_waiting_hint')}</Text>
              )}
            </View>
          ) : null}
          {renderSubtitleSourceSelector()}
          <View style={styles.publishOptionRow}>
            <View style={styles.publishOptionText}>
              <Text style={styles.optionLabel}>{t('publish_auto_correct_title')}</Text>
              <Text style={styles.optionHint} numberOfLines={2}>
                {autoCorrectActive
                  ? t('publish_auto_correct_on')
                  : t('publish_auto_correct_off')}
              </Text>
            </View>
            <Switch
              value={autoCorrectActive}
              onValueChange={updateAutoCorrectSubtitles}
              disabled={!selectedVideo}
              trackColor={{ false: '#e2e8f0', true: '#2563eb' }}
              thumbColor={autoCorrectActive ? '#f8fafc' : '#f1f5f9'}
            />
          </View>
          {autoCorrectActive ? (
            <Pressable style={styles.secondaryButton} onPress={openAutoCorrectPrompt}>
              <Text style={styles.secondaryButtonText}>{t('publish_auto_correct_edit_prompt')}</Text>
            </Pressable>
          ) : null}
          <View style={styles.publishOptionRow}>
            <View style={styles.publishOptionText}>
              <Text style={styles.optionLabel}>{t('publish_metadata_prompt_title')}</Text>
              <Text style={styles.optionHint} numberOfLines={2}>
                {useCorrectionPromptForMetadata
                  ? t('publish_metadata_prompt_on')
                  : t('publish_metadata_prompt_off')}
              </Text>
            </View>
            <Switch
              value={useCorrectionPromptForMetadata}
              onValueChange={updateUseCorrectionPromptForMetadata}
              disabled={!publishOptionsLoaded}
              trackColor={{ false: '#e2e8f0', true: '#2563eb' }}
              thumbColor={useCorrectionPromptForMetadata ? '#f8fafc' : '#f1f5f9'}
            />
          </View>
          {useCorrectionPromptForMetadata && metadataCorrectionPrompt ? (
            <Text style={styles.optionHint} numberOfLines={2}>
              {t('publish_metadata_prompt_using')}
            </Text>
          ) : null}
          {renderRunSelector(
            processRunMenuOpen,
            setProcessRunMenuOpen,
            t('publish_run_process_hint'),
          )}
          <Pressable
            style={[styles.secondaryButton, !selectedVideo && styles.btnDisabled]}
            onPress={openSubtitleCorrection}
            disabled={!selectedVideo}
          >
            <Text style={styles.secondaryButtonText}>{t('publish_correction_button')}</Text>
          </Pressable>
          <Pressable
            style={[styles.processButton, (!selectedVideo || processBusy) && styles.btnDisabled]}
            onPress={startProcess}
            disabled={!selectedVideo || processBusy}
          >
            <View style={styles.btnContent}>
              {processBusy && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
              <Text style={styles.processButtonText}>{processButtonLabel}</Text>
            </View>
          </Pressable>
          {processStatus ? (
            <Text style={[styles.status, toneStyle(processTone)]}>{processStatus}</Text>
          ) : null}
          <View style={styles.processPreviewBlock}>
            <Text style={styles.processPreviewTitle}>{t('publish_process_preview_title')}</Text>
            {renderPreviewSourceSelector()}
            {selectedPreviewUrl ? (
              <View style={styles.processPreviewVideoWrap}>
                {Platform.OS === 'web' ? (
                  React.createElement('video', {
                    src: selectedPreviewUrl,
                    style: { width: '100%', height: '100%', borderRadius: 12, objectFit: 'contain' },
                    controls: true,
                    muted: true,
                    playsInline: true,
                    preload: 'metadata',
                    onLoadedMetadata: updateSourceVideoDimensionsFromEvent,
                    poster: selectedPreviewPosterUrl || undefined,
                  })
                ) : (
                  <Image source={{ uri: selectedPreviewPosterUrl || selectedPreviewUrl }} style={styles.processPreviewImage} />
                )}
              </View>
            ) : (
              <Text style={styles.empty}>
                {selectedPreviewSource?.key === 'original'
                  ? t('publish_process_preview_empty')
                  : t('publish_preview_burn_empty')}
              </Text>
            )}
          </View>
          <View style={styles.processStatusBlock}>
            <View style={styles.processStatusHeader}>
              <Text style={styles.processStatusTitle}>{t('publish_process_status_title')}</Text>
              {processUpdatedAt ? (
                <Text style={styles.processStatusUpdated}>
                  {t('publish_process_status_updated', { value: formatTimestamp(processUpdatedAt) })}
                </Text>
              ) : null}
            </View>
            {processStatusLoading ? <ActivityIndicator style={{ marginTop: 8 }} /> : null}
            {processStatusError ? (
              <Text style={[styles.status, styles.statusBad]}>{processStatusError}</Text>
            ) : null}
            {processSteps ? (
              processStepDefinitions.map(({ key, label }) => {
                const step = processSteps[key];
                const status = step?.status || 'idle';
                const detail = step?.detail;
                return (
                  <View key={key} style={styles.processRow}>
                    <View style={styles.processRowHeader}>
                      <Text style={styles.processStepLabel}>{label}</Text>
                      <Text style={[styles.processStepStatus, processToneStyle(status)]}>
                        {processStatusLabel(status)}
                      </Text>
                    </View>
                    {detail ? <Text style={styles.processStepDetail}>{detail}</Text> : null}
                  </View>
                );
              })
            ) : (
              !processStatusLoading && !processStatusError ? (
                <Text style={styles.empty}>{t('publish_process_status_empty')}</Text>
              ) : null
            )}
          </View>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>{t('publish_cover_title')}</Text>
          <Text style={styles.sectionHint}>{t('publish_cover_hint')}</Text>
          <Pressable
            style={[
              styles.coverButton,
              (!selectedVideo || coverLoading || !processReadyForCover) && styles.btnDisabled,
            ]}
            onPress={extractCover}
            disabled={!selectedVideo || coverLoading || !processReadyForCover}
          >
            <View style={styles.btnContent}>
              {coverLoading && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
              <Text style={styles.coverButtonText}>{t('publish_cover_button')}</Text>
            </View>
          </Pressable>
          {selectedVideo && !processReadyForCover ? (
            <Text style={styles.helperText}>{t('publish_cover_disabled_hint')}</Text>
          ) : null}
          {coverUrl ? (
            <Image source={{ uri: coverUrl }} style={styles.coverPreview} resizeMode="contain" />
          ) : (
            <Text style={styles.empty}>{t('publish_cover_empty')}</Text>
          )}
          {coverStatus ? <Text style={[styles.status, toneStyle(coverTone)]}>{coverStatus}</Text> : null}
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>{t('publish_manual_title')}</Text>
          <Text style={styles.sectionHint}>{t('publish_manual_hint')}</Text>
          {renderRunSelector(
            publishRunMenuOpen,
            setPublishRunMenuOpen,
            t('publish_run_publish_hint'),
          )}
          <Pressable
            style={[
              styles.publishButton,
              (!selectedVideo || publishing) && styles.btnDisabled,
            ]}
            onPress={publishNow}
            disabled={!selectedVideo || publishing}
          >
            <View style={styles.btnContent}>
              {publishing && <ActivityIndicator color="white" style={{ marginRight: 8 }} />}
              <Text style={styles.publishButtonText}>{t('publish_button')}</Text>
            </View>
          </Pressable>
          {selectedVideo && !processReadyForPublish ? (
            <Text style={styles.helperText}>{t('publish_publish_disabled_hint')}</Text>
          ) : null}
          {publishStatus ? (
            <Text style={[styles.status, toneStyle(publishTone)]}>{publishStatus}</Text>
          ) : null}
          {publishZipUrl ? (
            <Text style={styles.zipText}>
              {t('publish_zip_ready', { value: publishZipUrl })}
            </Text>
          ) : null}
          <View style={styles.queueBlock}>
            <Pressable style={styles.queueHeaderButton} onPress={() => setQueueExpanded((prev) => !prev)}>
              <View style={styles.queueHeaderTextWrap}>
                <Text style={styles.queueTitle}>{t('publish_queue_title')}</Text>
                <Text style={styles.queueHint}>
                  {t('publish_queue_hint')}
                  {activeQueueCount ? ` (${activeQueueCount})` : ''}
                </Text>
              </View>
              <FontAwesome
                name={queueExpanded ? 'angle-up' : 'angle-down'}
                size={20}
                color="#0f172a"
              />
            </Pressable>
            {queueExpanded ? (
              <>
                {queueLoading ? <ActivityIndicator style={{ marginTop: 8 }} /> : null}
                {queueError ? (
                  <Text style={[styles.status, styles.statusBad]}>{queueError}</Text>
                ) : null}
                {publishQueue.length ? (
                  <ScrollView
                    style={styles.queueScroll}
                    contentContainerStyle={styles.queueScrollContent}
                    nestedScrollEnabled
                  >
                    {publishQueue.map((job) => {
                      const name =
                        job.title ||
                        (job.filename || '').replace(/\.zip$/i, '') ||
                        t('library_video_fallback', { id: job.id || '?' });
                      const metaParts = [queueStatusLabel(job.status)];
                      if (job.platforms?.length) metaParts.push(job.platforms.join(', '));
                      if (job.updated_at || job.created_at) {
                        metaParts.push(formatTimestamp(job.updated_at || job.created_at || ''));
                      }
                      return (
                        <View key={String(job.id || job.filename || name)} style={styles.queueRow}>
                          <Text style={styles.queueName} numberOfLines={1}>{name}</Text>
                          <Text style={styles.queueMeta} numberOfLines={2}>
                            {metaParts.filter(Boolean).join(' · ')}
                          </Text>
                          {job.detail ? (
                            <Text style={styles.queueDetail} numberOfLines={2}>{job.detail}</Text>
                          ) : null}
                          {job.error ? <Text style={styles.queueError}>{job.error}</Text> : null}
                        </View>
                      );
                    })}
                  </ScrollView>
                ) : !queueLoading && !queueError ? (
                  <Text style={styles.empty}>{t('publish_queue_empty')}</Text>
                ) : null}
              </>
            ) : null}
          </View>
        </View>
      </View>
      {Platform.OS === 'web' && previewVideoUrl
        ? React.createElement('video', {
            key: previewVideoUrl,
            src: previewVideoUrl,
            preload: 'metadata',
            muted: true,
            playsInline: true,
            onLoadedMetadata: updateSourceVideoDimensionsFromEvent,
            style: {
              display: 'none',
              width: 1,
              height: 1,
            },
          })
        : null}
      <Modal
        visible={portraitLayoutModalOpen}
        animationType="fade"
        transparent
        onRequestClose={() => setPortraitLayoutModalOpen(false)}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.portraitLayoutModal}>
            <View style={styles.modalHeader}>
              <Text style={styles.sectionTitle}>{t('publish_portrait_layout_modal_title')}</Text>
              <Pressable onPress={() => setPortraitLayoutModalOpen(false)} style={styles.modalClose}>
                <FontAwesome name="times" size={16} color="#0f172a" />
              </Pressable>
            </View>
            <Text style={styles.sectionHint}>{t('publish_portrait_layout_modal_hint')}</Text>
            {portraitLayoutMetrics ? (
              <View style={styles.portraitLayoutModalBody}>
                <View style={styles.portraitLayoutCanvas}>
                  <View
                    style={[
                      styles.portraitLayoutRegion,
                      styles.portraitLayoutTopRegion,
                      {
                        height: `${(portraitLayoutMetrics.top / portraitLayoutMetrics.outputHeight) * 100}%`,
                      },
                    ]}
                  >
                    <Text style={styles.portraitLayoutRegionText}>{t('publish_portrait_layout_top')}</Text>
                  </View>
                  <View
                    style={[
                      styles.portraitLayoutForegroundSlot,
                      {
                        top: `${(portraitLayoutMetrics.top / portraitLayoutMetrics.outputHeight) * 100}%`,
                        height: `${(portraitLayoutMetrics.foregroundHeight / portraitLayoutMetrics.outputHeight) * 100}%`,
                      },
                    ]}
                  >
                    <View
                      style={[
                        styles.portraitLayoutForeground,
                        {
                          width: `${(portraitLayoutMetrics.foregroundWidth / portraitLayoutMetrics.outputWidth) * 100}%`,
                        },
                      ]}
                    >
                      <Text style={styles.portraitLayoutForegroundText}>
                        {portraitLayoutMetrics.foregroundWidth}x{portraitLayoutMetrics.foregroundHeight}
                      </Text>
                    </View>
                  </View>
                  <View
                    style={[
                      styles.portraitLayoutRegion,
                      styles.portraitLayoutBottomRegion,
                      {
                        top: `${((portraitLayoutMetrics.outputHeight - portraitLayoutMetrics.bottom) / portraitLayoutMetrics.outputHeight) * 100}%`,
                        height: `${(portraitLayoutMetrics.bottom / portraitLayoutMetrics.outputHeight) * 100}%`,
                      },
                    ]}
                  >
                    <Text style={styles.portraitLayoutRegionText}>{t('publish_portrait_layout_bottom')}</Text>
                  </View>
                </View>
                <View style={styles.portraitLayoutDetails}>
                  <Text style={styles.optionLabel}>
                    {portraitLayoutMetrics.outputWidth}x{portraitLayoutMetrics.outputHeight}
                  </Text>
                  <Text style={styles.optionHint}>
                    {t('publish_portrait_layout_source', {
                      width: String(portraitLayoutMetrics.sourceWidth),
                      height: String(portraitLayoutMetrics.sourceHeight),
                    })}
                  </Text>
                  <Text style={styles.optionHint}>
                    {t('publish_portrait_layout_top')}: {portraitLayoutMetrics.top}px · {formatMetricPercent(portraitLayoutMetrics.top / portraitLayoutMetrics.outputHeight)}
                  </Text>
                  <Text style={styles.optionHint}>
                    {t('publish_portrait_layout_bottom')}: {portraitLayoutMetrics.bottom}px · {formatMetricPercent(portraitLayoutMetrics.bottom / portraitLayoutMetrics.outputHeight)}
                  </Text>
                  <Text style={styles.optionHint}>
                    {t('publish_portrait_layout_shift', {
                      value: `${portraitLayoutMetrics.centerShift}px`,
                      ratio: formatPortraitBottomSpaceRatio(portraitLayoutMetrics.centerShiftRatio),
                    })}
                  </Text>
                  {portraitLayoutMetrics.narrowed ? (
                    <Text style={styles.optionHint}>{t('publish_portrait_layout_narrowed')}</Text>
                  ) : null}
                </View>
              </View>
            ) : (
              <Text style={styles.empty}>{t('publish_portrait_layout_waiting_hint')}</Text>
            )}
          </View>
        </View>
      </Modal>
      <Modal
        visible={!!confirmDeleteVideo}
        animationType="fade"
        transparent
        onRequestClose={() => {
          if (!deleteVideoPending) {
            setConfirmDeleteVideo(null);
            setDeleteVideoError('');
          }
        }}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.deleteVideoModal}>
            <Text style={styles.sectionTitle}>{t('library_delete_title')}</Text>
            <Text style={styles.sectionHint}>{t('library_delete_body')}</Text>
            {confirmDeleteVideo ? (
              <Text style={styles.deleteVideoName} numberOfLines={3}>
                {confirmDeleteVideo.title || confirmDeleteVideo.file_path}
              </Text>
            ) : null}
            {deleteVideoError ? (
              <Text style={[styles.status, styles.statusBad]}>{deleteVideoError}</Text>
            ) : null}
            <View style={styles.deleteVideoActions}>
              <Pressable
                style={styles.secondaryButton}
                onPress={() => {
                  if (deleteVideoPending) return;
                  setConfirmDeleteVideo(null);
                  setDeleteVideoError('');
                }}
                disabled={deleteVideoPending}
              >
                <Text style={styles.secondaryButtonText}>{t('library_menu_cancel')}</Text>
              </Pressable>
              <Pressable
                style={[styles.deleteVideoConfirmButton, deleteVideoPending && styles.btnDisabled]}
                onPress={confirmDeleteSelectedVideo}
                disabled={deleteVideoPending}
              >
                <View style={styles.btnContent}>
                  {deleteVideoPending && <ActivityIndicator color="#b91c1c" style={{ marginRight: 8 }} />}
                  <Text style={styles.deleteVideoConfirmText}>
                    {deleteVideoPending ? t('library_delete_pending') : t('library_delete_confirm')}
                  </Text>
                </View>
              </Pressable>
            </View>
          </View>
        </View>
      </Modal>
      <Modal
        visible={autoCorrectPromptOpen}
        animationType="fade"
        transparent
        onRequestClose={cancelAutoCorrectPrompt}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.autoCorrectModal}>
            <View style={styles.modalHeader}>
              <Text style={styles.sectionTitle}>{t('publish_auto_correct_modal_title')}</Text>
              <Pressable onPress={cancelAutoCorrectPrompt} style={styles.modalClose}>
                <FontAwesome name="times" size={16} color="#0f172a" />
              </Pressable>
            </View>
            <Text style={styles.sectionHint}>{t('publish_auto_correct_modal_hint')}</Text>
            <TextInput
              value={autoCorrectDraftPrompt}
              onChangeText={(value) => {
                setAutoCorrectDraftPrompt(value);
                if (value.trim()) setAutoCorrectPromptError('');
              }}
              multiline
              placeholder={t('publish_auto_correct_prompt_placeholder')}
              style={styles.promptInput}
            />
            {autoCorrectPromptError ? (
              <Text style={[styles.status, styles.statusBad]}>{autoCorrectPromptError}</Text>
            ) : null}
            <View style={styles.correctionButtonRow}>
              <Pressable style={styles.secondaryButton} onPress={cancelAutoCorrectPrompt}>
                <Text style={styles.secondaryButtonText}>{t('button_cancel')}</Text>
              </Pressable>
              <Pressable
                style={[
                  styles.processButton,
                  !autoCorrectDraftPrompt.trim() && styles.btnDisabled,
                ]}
                onPress={saveAutoCorrectPrompt}
                disabled={!autoCorrectDraftPrompt.trim()}
              >
                <Text style={styles.processButtonText}>{t('button_save')}</Text>
              </Pressable>
            </View>
          </View>
        </View>
      </Modal>
      <Modal visible={correctionOpen} animationType="fade" transparent onRequestClose={() => setCorrectionOpen(false)}>
        <View style={styles.modalBackdrop}>
          <View style={styles.correctionModal}>
            <View style={styles.modalHeader}>
              <Text style={styles.sectionTitle}>{t('publish_correction_title')}</Text>
              <Pressable onPress={() => setCorrectionOpen(false)} style={styles.modalClose}>
                <FontAwesome name="times" size={16} color="#0f172a" />
              </Pressable>
            </View>
            <Text style={styles.sectionHint}>{t('publish_correction_hint')}</Text>
            <View style={styles.correctionSourceRow}>
              <Text style={styles.optionLabel}>{t('publish_correction_source_title')}</Text>
              <View style={styles.languageChipGroup}>
                {subtitleSourceOptions.map((option) => {
                  const active = correctionSourceVariant === option.key;
                  return (
                    <Pressable
                      key={option.key}
                      style={[styles.languageChip, active && styles.languageChipActive]}
                      onPress={() => setCorrectionSourceVariant(option.key)}
                      disabled={correctionSaving || correctionLoading}
                    >
                      <Text style={[styles.languageChipText, active && styles.languageChipTextActive]}>
                        {option.label}
                      </Text>
                    </Pressable>
                  );
                })}
              </View>
              <Text style={styles.optionHint}>
                {correctionSourceVariant === 'polished'
                  ? t('publish_correction_source_polished_hint')
                  : t('publish_correction_source_original_hint')}
              </Text>
            </View>
            <TextInput
              value={correctionPrompt}
              onChangeText={setCorrectionPrompt}
              multiline
              placeholder={t('publish_correction_prompt_placeholder')}
              style={styles.promptInput}
            />
            <View style={styles.correctionButtonRow}>
              <Pressable
                style={[styles.secondaryButton, correctionSaving && styles.btnDisabled]}
                onPress={() => runCorrectionAction('ai')}
                disabled={correctionSaving || correctionLoading}
              >
                <Text style={styles.secondaryButtonText}>{t('publish_correction_ai')}</Text>
              </Pressable>
              <Pressable
                style={[styles.secondaryButton, correctionSaving && styles.btnDisabled]}
                onPress={() => runCorrectionAction('save_original')}
                disabled={correctionSaving || correctionLoading}
              >
                <Text style={styles.secondaryButtonText}>{t('publish_correction_save_original')}</Text>
              </Pressable>
              <Pressable
                style={[styles.secondaryButton, correctionSaving && styles.btnDisabled]}
                onPress={() => runCorrectionAction('save_polished')}
                disabled={correctionSaving || correctionLoading}
              >
                <Text style={styles.secondaryButtonText}>{t('publish_correction_save_polished')}</Text>
              </Pressable>
            </View>
            {correctionLoading || correctionSaving ? <ActivityIndicator style={{ marginTop: 10 }} /> : null}
            {correctionStatus ? <Text style={styles.status}>{correctionStatus}</Text> : null}
            <ScrollView style={styles.correctionScroll} nestedScrollEnabled>
              <Text style={styles.optionLabel}>{t('publish_correction_original')}</Text>
              <TextInput
                value={originalSubtitleText}
                onChangeText={setOriginalSubtitleText}
                multiline
                style={styles.subtitleEditor}
              />
              <Text style={[styles.optionLabel, { marginTop: 12 }]}>{t('publish_correction_polished')}</Text>
              <TextInput
                value={polishedSubtitleText}
                onChangeText={setPolishedSubtitleText}
                multiline
                style={styles.subtitleEditor}
              />
            </ScrollView>
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scrollContent: {
    padding: 16,
    paddingBottom: 32,
  },
  container: {
    flex: 1,
    width: '100%',
    maxWidth: 720,
    alignSelf: 'center',
  },
  title: { fontSize: 22, fontWeight: '700', color: '#0f172a' },
  sub: { marginTop: 8, color: '#334155' },
  modeToggleRow: {
    marginTop: 14,
    flexDirection: 'row',
    gap: 8,
  },
  modeToggleButton: {
    minHeight: 34,
    paddingHorizontal: 12,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#cbd5e1',
    backgroundColor: '#f8fafc',
    flexDirection: 'row',
    alignItems: 'center',
    gap: 7,
  },
  modeToggleButtonActive: {
    borderColor: '#0f172a',
    backgroundColor: '#0f172a',
  },
  modeToggleText: { fontSize: 12, fontWeight: '800', color: '#0f172a' },
  modeToggleTextActive: { color: 'white' },
  card: {
    marginTop: 16,
    padding: 16,
    borderRadius: 16,
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: '#0f172a' },
  sectionHint: { marginTop: 6, fontSize: 12, color: '#64748b' },
  videoListScroll: {
    marginTop: 12,
    maxHeight: 420,
  },
  videoList: { gap: 12, paddingBottom: 4 },
  videoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 10,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
  },
  videoRowActive: {
    borderColor: '#2563eb',
    backgroundColor: '#eff6ff',
  },
  videoPreview: {
    width: 110,
    height: 70,
    borderRadius: 10,
    backgroundColor: '#0f172a',
    marginRight: 12,
    justifyContent: 'center',
    alignItems: 'center',
    overflow: 'hidden',
  },
  previewLabel: { color: '#cbd5f5', fontSize: 11, fontWeight: '600' },
  videoMeta: { flex: 1 },
  videoTitle: { fontSize: 15, fontWeight: '600', color: '#0f172a' },
  videoPath: { color: '#64748b', fontSize: 11 },
  videoTime: { color: '#334155', fontSize: 11, marginTop: 4 },
  videoActions: {
    marginLeft: 8,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
  },
  selectBadge: {
    width: 22,
    height: 22,
    borderRadius: 11,
    borderWidth: 1,
    borderColor: '#cbd5f5',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'white',
  },
  selectBadgeActive: {
    backgroundColor: '#2563eb',
    borderColor: '#2563eb',
  },
  videoDeleteButton: {
    width: 28,
    height: 28,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#fee2e2',
  },
  moreButton: {
    marginTop: 4,
    marginBottom: 4,
    alignSelf: 'center',
    paddingHorizontal: 18,
    paddingVertical: 8,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#cbd5f5',
    backgroundColor: '#f8fafc',
  },
  moreButtonText: { fontSize: 12, fontWeight: '700', color: '#0f172a' },
  footerSpacer: { height: 8 },
  platformGrid: {
    marginTop: 12,
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  platformChip: {
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#cbd5f5',
    backgroundColor: '#f8fafc',
  },
  platformChipActive: {
    borderColor: '#0f172a',
    backgroundColor: '#0f172a',
  },
  platformText: { fontSize: 12, fontWeight: '600', color: '#1e293b' },
  platformTextActive: { color: '#f8fafc' },
  selectedText: { marginTop: 12, fontSize: 12, color: '#0f172a' },
  musicFieldGrid: {
    marginTop: 12,
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  musicField: {
    minWidth: 220,
    flex: 1,
  },
  musicFieldWide: {
    width: '100%',
  },
  fieldInput: {
    marginTop: 6,
    minHeight: 36,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#cbd5e1',
    backgroundColor: '#f8fafc',
    paddingHorizontal: 10,
    paddingVertical: 8,
    fontSize: 12,
    color: '#0f172a',
  },
  fieldInputMultiline: {
    marginTop: 6,
    minHeight: 82,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#cbd5e1',
    backgroundColor: '#f8fafc',
    paddingHorizontal: 10,
    paddingVertical: 8,
    fontSize: 12,
    color: '#0f172a',
    textAlignVertical: 'top',
  },
  musicActions: {
    marginTop: 2,
  },
  publishOptionRow: {
    marginTop: 12,
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 12,
  },
  publishOptionText: { flex: 1 },
  optionLabel: { fontSize: 12, fontWeight: '700', color: '#0f172a' },
  optionHint: { marginTop: 4, fontSize: 11, color: '#64748b' },
  languageOptionRow: {
    marginTop: 8,
    minHeight: 38,
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  languageChipGroup: {
    flex: 1,
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'flex-end',
    gap: 6,
  },
  languageChip: {
    minWidth: 44,
    height: 26,
    borderRadius: 13,
    borderWidth: 1,
    borderColor: '#cbd5f5',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'white',
  },
  languageChipActive: {
    backgroundColor: '#0f172a',
    borderColor: '#0f172a',
  },
  languageChipText: { fontSize: 11, fontWeight: '700', color: '#0f172a' },
  languageChipTextActive: { color: 'white' },
  liftRatioRow: {
    marginTop: 8,
    minHeight: 42,
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
    flexDirection: 'row',
    flexWrap: 'wrap',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 10,
  },
  liftRatioControls: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end',
    flexShrink: 0,
    gap: 6,
  },
  liftRatioButton: {
    minWidth: 30,
    height: 28,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#cbd5e1',
    backgroundColor: 'white',
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 8,
  },
  liftRatioButtonText: { fontSize: 12, fontWeight: '800', color: '#0f172a' },
  liftRatioInput: {
    width: 58,
    height: 30,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#cbd5e1',
    backgroundColor: 'white',
    paddingHorizontal: 8,
    fontSize: 12,
    fontWeight: '700',
    color: '#0f172a',
    textAlign: 'center',
  },
  liftRatioInputDisabled: {
    backgroundColor: '#f1f5f9',
    color: '#94a3b8',
  },
  miniButton: {
    minHeight: 30,
    paddingHorizontal: 10,
    paddingVertical: 7,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: '#cbd5e1',
    backgroundColor: 'white',
    alignItems: 'center',
    justifyContent: 'center',
  },
  miniButtonText: { fontSize: 11, fontWeight: '800', color: '#0f172a' },
  portraitMetricsCard: {
    marginTop: 8,
    padding: 10,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#dbeafe',
    backgroundColor: '#eff6ff',
    gap: 8,
  },
  portraitMetricsHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 10,
  },
  portraitMetricRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  portraitMetricChip: {
    flex: 1,
    minWidth: 120,
    paddingHorizontal: 9,
    paddingVertical: 8,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#bfdbfe',
    backgroundColor: 'white',
  },
  portraitMetricLabel: { fontSize: 10, fontWeight: '800', color: '#1e40af', textTransform: 'uppercase' },
  portraitMetricValue: { marginTop: 3, fontSize: 12, fontWeight: '800', color: '#0f172a' },
  subtitleStyleRow: {
    marginTop: 8,
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  subtitleStyleSwitch: {
    minWidth: 190,
    flex: 1,
    minHeight: 42,
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 10,
  },
  subtitleColorRow: {
    marginTop: 8,
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  subtitleColorField: {
    minWidth: 180,
    flex: 1,
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
  },
  colorControl: {
    marginTop: 8,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  colorSwatch: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#cbd5e1',
  },
  colorInput: {
    flex: 1,
    minWidth: 92,
    height: 30,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#cbd5e1',
    backgroundColor: 'white',
    paddingHorizontal: 8,
    fontSize: 12,
    fontWeight: '700',
    color: '#0f172a',
  },
  runSelectorBlock: {
    marginTop: 10,
    padding: 10,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
  },
  runSelectorButton: {
    marginTop: 8,
    minHeight: 46,
    paddingVertical: 8,
    paddingHorizontal: 10,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#cbd5e1',
    backgroundColor: 'white',
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  runSelectorText: { flex: 1 },
  runSelectorLabel: { fontSize: 12, fontWeight: '700', color: '#0f172a' },
  runSelectorHint: { marginTop: 2, fontSize: 11, color: '#64748b' },
  runDropdown: {
    marginTop: 8,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#dbe3ef',
    backgroundColor: 'white',
    overflow: 'hidden',
  },
  runDropdownScroll: {
    maxHeight: 220,
  },
  runOptionRow: {
    padding: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#edf2f7',
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  runOptionRowActive: {
    backgroundColor: '#eff6ff',
  },
  runOptionMain: { flex: 1 },
  runOptionLabel: { fontSize: 12, fontWeight: '700', color: '#0f172a' },
  runOptionLabelActive: { color: '#1d4ed8' },
  runOptionHint: { marginTop: 2, fontSize: 11, color: '#64748b' },
  secondaryButton: {
    marginTop: 10,
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#cbd5f5',
    backgroundColor: '#f8fafc',
    alignItems: 'center',
  },
  secondaryButtonText: { fontSize: 12, fontWeight: '700', color: '#0f172a' },
  sessionBlock: {
    marginTop: 10,
    padding: 10,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
  },
  sessionRow: {
    marginTop: 8,
    padding: 8,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: 'white',
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  sessionRowActive: {
    borderColor: '#2563eb',
    backgroundColor: '#eff6ff',
  },
  sessionMain: { flex: 1 },
  sessionName: { fontSize: 12, fontWeight: '700', color: '#0f172a' },
  sessionMeta: { marginTop: 2, fontSize: 11, color: '#64748b' },
  sessionDelete: {
    width: 28,
    height: 28,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#fee2e2',
  },
  coverButton: {
    marginTop: 12,
    backgroundColor: '#0f172a',
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
  },
  coverButtonText: { color: 'white', fontWeight: '700' },
  coverPreview: {
    marginTop: 12,
    width: '100%',
    height: 180,
    borderRadius: 14,
    backgroundColor: '#0f172a',
    overflow: 'hidden',
  },
  processButton: {
    marginTop: 12,
    backgroundColor: '#0f172a',
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
  },
  processButtonText: { color: 'white', fontWeight: '700' },
  processPreviewBlock: {
    marginTop: 12,
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
  },
  processPreviewTitle: { fontSize: 13, fontWeight: '600', color: '#0f172a' },
  previewSourceBlock: {
    marginTop: 8,
  },
  processPreviewVideoWrap: {
    marginTop: 8,
    width: '100%',
    height: 200,
    borderRadius: 12,
    overflow: 'hidden',
    backgroundColor: '#0f172a',
  },
  processPreviewImage: { width: '100%', height: '100%' },
  processStatusBlock: {
    marginTop: 12,
    padding: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
  },
  processStatusHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  processStatusTitle: { fontSize: 13, fontWeight: '600', color: '#0f172a' },
  processStatusUpdated: { fontSize: 11, color: '#64748b' },
  processRow: { marginTop: 10 },
  processRowHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  processStepLabel: { fontSize: 12, fontWeight: '600', color: '#0f172a' },
  processStepStatus: { fontSize: 11, fontWeight: '600' },
  processStepDetail: { marginTop: 4, fontSize: 11, color: '#64748b' },
  empty: { marginTop: 12, color: '#64748b', fontSize: 12 },
  helperText: { marginTop: 8, fontSize: 12, color: '#64748b' },
  publishButton: {
    marginTop: 12,
    backgroundColor: '#2563eb',
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
  },
  publishButtonText: { color: 'white', fontWeight: '700' },
  btnDisabled: { opacity: 0.6 },
  btnContent: { flexDirection: 'row', alignItems: 'center' },
  status: { marginTop: 10, fontSize: 12 },
  statusNeutral: { color: '#0f172a' },
  statusGood: { color: '#15803d' },
  statusBad: { color: '#b91c1c' },
  statusWarning: { color: '#b45309' },
  zipText: { marginTop: 8, fontSize: 12, color: '#475569' },
  queueBlock: {
    marginTop: 16,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#e2e8f0',
  },
  queueHeaderButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 12,
  },
  queueHeaderTextWrap: {
    flex: 1,
  },
  queueTitle: { fontSize: 14, fontWeight: '700', color: '#0f172a' },
  queueHint: { marginTop: 6, fontSize: 12, color: '#64748b' },
  queueScroll: {
    marginTop: 10,
    maxHeight: 320,
  },
  queueScrollContent: {
    paddingBottom: 4,
  },
  queueRow: {
    marginTop: 10,
    padding: 10,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    backgroundColor: '#f8fafc',
  },
  queueName: { fontSize: 12, fontWeight: '600', color: '#0f172a' },
  queueMeta: { marginTop: 4, fontSize: 11, color: '#475569' },
  queueDetail: { marginTop: 4, fontSize: 11, color: '#334155' },
  queueError: { marginTop: 4, fontSize: 11, color: '#b91c1c' },
  modalBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(15, 23, 42, 0.45)',
    padding: 16,
    justifyContent: 'center',
  },
  correctionModal: {
    width: '100%',
    maxWidth: 920,
    maxHeight: '92%',
    alignSelf: 'center',
    padding: 16,
    borderRadius: 16,
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  autoCorrectModal: {
    width: '100%',
    maxWidth: 560,
    alignSelf: 'center',
    padding: 16,
    borderRadius: 16,
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  portraitLayoutModal: {
    width: '100%',
    maxWidth: 640,
    alignSelf: 'center',
    padding: 16,
    borderRadius: 16,
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  portraitLayoutModalBody: {
    marginTop: 14,
    flexDirection: 'row',
    flexWrap: 'wrap',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 16,
  },
  portraitLayoutCanvas: {
    width: 210,
    height: 373,
    borderRadius: 18,
    backgroundColor: '#0f172a',
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#1e293b',
    position: 'relative',
  },
  portraitLayoutRegion: {
    position: 'absolute',
    left: 0,
    right: 0,
    alignItems: 'center',
    justifyContent: 'center',
  },
  portraitLayoutTopRegion: {
    top: 0,
    backgroundColor: 'rgba(96, 165, 250, 0.28)',
  },
  portraitLayoutBottomRegion: {
    backgroundColor: 'rgba(34, 197, 94, 0.28)',
  },
  portraitLayoutRegionText: {
    fontSize: 11,
    fontWeight: '800',
    color: '#e0f2fe',
    textShadowColor: 'rgba(15,23,42,0.65)',
    textShadowRadius: 3,
  },
  portraitLayoutForegroundSlot: {
    position: 'absolute',
    left: 0,
    right: 0,
    alignItems: 'center',
    justifyContent: 'center',
  },
  portraitLayoutForeground: {
    height: '100%',
    borderWidth: 2,
    borderColor: '#f8fafc',
    backgroundColor: '#475569',
    alignItems: 'center',
    justifyContent: 'center',
  },
  portraitLayoutForegroundText: {
    fontSize: 12,
    fontWeight: '800',
    color: 'white',
  },
  portraitLayoutDetails: {
    minWidth: 220,
    flex: 1,
    gap: 6,
  },
  deleteVideoModal: {
    width: '100%',
    maxWidth: 420,
    alignSelf: 'center',
    padding: 16,
    borderRadius: 16,
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  deleteVideoName: {
    marginTop: 12,
    padding: 10,
    borderRadius: 12,
    backgroundColor: '#f8fafc',
    borderWidth: 1,
    borderColor: '#e2e8f0',
    color: '#0f172a',
    fontSize: 12,
  },
  deleteVideoActions: {
    marginTop: 12,
    flexDirection: 'row',
    justifyContent: 'flex-end',
    flexWrap: 'wrap',
    gap: 8,
  },
  deleteVideoConfirmButton: {
    marginTop: 10,
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#fecaca',
    backgroundColor: '#fee2e2',
    alignItems: 'center',
  },
  deleteVideoConfirmText: { fontSize: 12, fontWeight: '700', color: '#b91c1c' },
  modalHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 12,
  },
  modalClose: {
    width: 32,
    height: 32,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f8fafc',
  },
  promptInput: {
    marginTop: 12,
    minHeight: 72,
    padding: 10,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#cbd5f5',
    color: '#0f172a',
    backgroundColor: '#f8fafc',
    textAlignVertical: 'top',
  },
  correctionSourceRow: {
    marginTop: 12,
    gap: 8,
  },
  correctionButtonRow: {
    marginTop: 10,
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  correctionScroll: {
    marginTop: 12,
    maxHeight: 520,
  },
  subtitleEditor: {
    marginTop: 8,
    minHeight: 180,
    padding: 10,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#cbd5f5',
    color: '#0f172a',
    backgroundColor: '#f8fafc',
    fontFamily: Platform.OS === 'web' ? 'monospace' : undefined,
    fontSize: 12,
    textAlignVertical: 'top',
  },
});
