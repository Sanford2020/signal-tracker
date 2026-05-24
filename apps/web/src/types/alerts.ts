export type AlertSummary = {
  id: string;
  intel_file_id: string;
  intel_file_title: string;
  alert_type: string;
  severity: string;
  message: string;
  status: string;
  created_at: string;
};

export type AlertListData = {
  items: AlertSummary[];
  total: number;
};

export type AlertUpdateRequest = {
  status: "acknowledged" | "dismissed";
};
