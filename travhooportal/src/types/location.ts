interface Location {
  id: string;
  name: string;
  description?: {
    short?: string;
    long?: string;
    title?: string;
    history?: string;
  };
  type?: string;
  tagline?: string;
  images?: {
    banner: string;
    card?: string;
    others?: string[];
  };
  labels?: Array<{
    name: string;
    id: string;
  }>;
  locations?: Array<{
    country: { name: string; id: string };
    state?: { name: string; id: string };
    city?: { name: string; id: string };
    region?: { name: string; id: string };
  }>;
}

interface Experience {
  name: string;
  type: string;
  images?: {
    banner: string;
    card?: string;
    others?: string[];
  };
  description?: {
    short?: string;
    long?: string;
  };
  locations?: Array<{
    country: { name: string; id: string };
    state?: { name: string; id: string };
    city?: { name: string; id: string };
    region?: { name: string; id: string };
  }>;
}

interface City {
  id: string;
  name: string;
  description?: {
    short?: string;
    long?: string;
    title?: string;
    history?: string;
  };
  greetingText?: string;
  tagline?: string;
  images?: {
    banner: string;
    card?: string;
    others?: string[];
  };
  labels?: Array<{
    name: string;
    id: string;
  }>;
  locations?: Array<{
    country: { name: string; id: string };
    state?: { name: string; id: string };
    city?: { name: string; id: string };
    region?: { name: string; id: string };
  }>;
  emergencyContacts?: {
    Police?: string;
    Ambulance?: string;
    Fire?: string;
    'Tourist Helpline'?: string;
    'State Tourism'?: string;
  };
  experiences?: {
    Food?: Experience[];
    Activities?: Experience[];
    LocalMarkets?: Experience[];
    Spiritual?: Experience[];
    Historical?: Experience[];
    Nature?: Experience[];
    Cultural?: Experience[];
    Adventure?: Experience[];
    Others?: Experience[];
  };
  safetyInformation?: string[];
  travelTips?: string[];
}

interface State {
  id: string;
  name: string;
  description?: {
    short?: string;
    long?: string;
    title?: string;
    history?: string;
  };
  greetingText?: string;
  tagline?: string;
  images?: {
    banner: string;
    card?: string;
    others?: string[];
  };
  labels?: Array<{
    name: string;
    id: string;
  }>;
  locations?: Array<{
    country: { name: string; id: string };
    state?: { name: string; id: string };
    city?: { name: string; id: string };
    region?: { name: string; id: string };
  }>;
  emergencyContacts?: {
    Police?: string;
    Ambulance?: string;
    Fire?: string;
    'Tourist Helpline'?: string;
    'State Tourism'?: string;
  };
  experiences?: {
    Food?: Experience[];
    Activities?: Experience[];
    LocalMarkets?: Experience[];
    Spiritual?: Experience[];
    Historical?: Experience[];
    Nature?: Experience[];
    Cultural?: Experience[];
    Adventure?: Experience[];
    Others?: Experience[];
  };
  safetyInformation?: string[];
  travelTips?: string[];
}

export type { Location, City, State, Experience };
