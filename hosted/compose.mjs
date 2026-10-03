// Operator-owned templates. No caller-supplied Docker commands, mounts or images.
export function workspaceCompose({ id }, config, bootstrap) {
  if(!/^[a-z0-9-]{24}$/.test(id))throw Error('Invalid workspace ID');
  const name=`le-${id}`;
  return {
    name,
    services:{
      database:{image:config.postgresImage||'postgres:16-bookworm',restart:'unless-stopped',
        logging:{driver:'json-file',options:{'max-size':'5m','max-file':'2'}},
        environment:{POSTGRES_USER:'lazyedit',POSTGRES_DB:'lazyedit',POSTGRES_PASSWORD_FILE:'/run/secrets/db_password'},
        secrets:['db_password'],volumes:['database:/var/lib/postgresql/data'],networks:['private'],
        healthcheck:{test:['CMD-SHELL','pg_isready -U lazyedit'],interval:'5s',timeout:'3s',retries:20},
        mem_limit:'512m',cpus:0.5,pids_limit:128},
      worker:{image:config.workerImage||'lazyedit-workspace:local',init:true,restart:'unless-stopped',
        logging:{driver:'json-file',options:{'max-size':'10m','max-file':'3'}},
        container_name:`${name}-worker`,hostname:`${name}-worker`,tmpfs:['/tmp:size=512m','/run:size=16m'],
        user:'1000:1000',cap_drop:['ALL'],security_opt:['no-new-privileges:true'],
        shm_size:'1gb',mem_limit:config.workerMemory||'8g',cpus:config.workerCPUs||2,pids_limit:768,
        environment:{HOME:'/state/home',DISPLAY:':99',AUTOPUBLISH_DATA_ROOT:'/state/publisher',
          AUTOPUBLISH_QUEUE_JOURNAL:'/state/publisher/queue.json',AUTOPUBLISH_DISPLAY:':99',AUTOPUBLISH_ACCOUNT_NEUTRAL:'1',
          AUTOPUBLISH_BROWSER_BIN:'/usr/bin/chromium',AUTOPUBLISH_CHROMEDRIVER:'/usr/bin/chromedriver',
          AUTOPUBLISH_CHROMIUM_FLAGS:'--no-sandbox --kiosk --disable-dev-shm-usage --password-store=basic --disable-session-crashed-bubble',
          LAZYEDIT_UPLOAD_DIR:'/state/data',LAZYEDIT_PORT:'18787',LAZYEDIT_BIND:'127.0.0.1',LAZYEDIT_AUTORELOAD:'0',
          LAZYEDIT_AUTOPUBLISH_URL:'http://127.0.0.1:8081/publish',LAZYEDIT_WHISPER_PYTHON:'/opt/venv/bin/python',
          LAZYEDIT_LOCAL_PACKAGE_ROOT:'/state/data',AUTOPUBLISH_LOCAL_PACKAGE_ROOT:'/state/data',
          LAZYEDIT_CAPTION_PYTHON:'/opt/venv/bin/python',LAZYEDIT_WHISPER_MODEL:'small',LAZYEDIT_WHISPER_MODEL_CANDIDATES:'small,base',
          CUDA_VISIBLE_DEVICES:'',OMP_NUM_THREADS:'2',OPENBLAS_NUM_THREADS:'2',PYTHONUNBUFFERED:'1',
          LAZYEDIT_HOSTED:'1',...(config.sampleFile&&config.sampleSha256?{LAZYEDIT_SAMPLE_SHA256:config.sampleSha256}:{})},
        volumes:['workspace:/state',`${bootstrap}:/bootstrap:ro`,...(config.sampleFile&&config.sampleSha256?[`${config.sampleFile}:/samples/vancouver.mp4:ro`]:[])],secrets:['db_password'],
        networks:{private:{},front:{aliases:[`${name}-worker`]}},
        depends_on:{database:{condition:'service_healthy'}},
        healthcheck:{test:['CMD','node','/opt/lazyedit/hosted/health.mjs'],interval:'30s',timeout:'5s',retries:5,start_period:'60s'},
      }
    },
    networks:{private:{internal:true},front:{external:true,name:config.network||'lazyedit-hosted'}},
    volumes:{database:{},workspace:{}},
    secrets:{db_password:{file:`${bootstrap}/db_password`}},
  };
}
