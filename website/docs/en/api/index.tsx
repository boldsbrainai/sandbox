export const frontmatter = {
  pageType: 'custom',
};

import { useDark, useI18n } from '@rspress/core/runtime';
import { ApiReferenceReact } from '@scalar/api-reference-react';
import { Suspense } from 'react';
import './index.scss';

import '@scalar/api-reference-react/style.css';

export const APIPage = () => {
  const dark = useDark();
  const t = useI18n();

  return (
    <div className="api-page">
      <div className="api-page__intro">
        <div>
          <p className="api-page__eyebrow">API documentation</p>
          <h1 className="api-page__title">Reference and overview</h1>
          <p className="api-page__description">
            Browse the full interactive API reference below or start with the
            overview for authentication, domain breakdown, and common agent
            workflows.
          </p>
        </div>
        <a className="api-page__link" href="/en/api/overview">
          Open API overview
        </a>
      </div>

      <Suspense
        fallback={
          <div className="api-page__loading">
            <div className="api-page__spinner" />
            <div className="api-page__loading-text">
              {t('loadingApiReference')}
            </div>
          </div>
        }
      >
        <ApiReferenceReact
          key={dark ? 'dark' : 'light'}
          configuration={{
            baseServerURL: 'http://127.0.0.1:8080',
            url: '/v1/openapi.json',
            darkMode: dark,
            forceDarkModeState: dark ? 'dark' : 'light',
            hideTestRequestButton: true,
            hideDownloadButton: true,
            hideDarkModeToggle: true,
            hideClientButton: true,
            hideModels: true,
            telemetry: false,
            documentDownloadType: 'json',
          }}
        />
      </Suspense>
    </div>
  );
};

export default APIPage;
