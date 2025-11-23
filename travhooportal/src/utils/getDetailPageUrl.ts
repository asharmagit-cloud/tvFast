import { TYPE_TO_PAGE_MAP } from '../constants';

const getDetailPageUrl = (id: string, type: string) => {
  return `/detail/${TYPE_TO_PAGE_MAP.detail[type as keyof typeof TYPE_TO_PAGE_MAP.detail]}/${id}`;
};

export default getDetailPageUrl;
