{ pkgs }: 
let

    nginxModified = pkgs.nginx.overrideAttrs (oldAttrs: rec {
        configureFlags = oldAttrs.configureFlags ++ [
            "--http-client-body-temp-path=/home/runner/workspace/cache/client_body"
            "--http-proxy-temp-path=/home/runner/workspace/cache/proxy"
            "--http-fastcgi-temp-path=/home/runner/workspace/cache/fastcgi"
            "--http-uwsgi-temp-path=/home/runner/workspace/cache/uwsgi"
            "--http-scgi-temp-path=/home/runner/workspace/cache/scgi"
         ];
    });

in {
	deps = [
		nginxModified
        pkgs.python39
        pkgs.python39Packages.flask
        pkgs.python39Packages.waitress
        pkgs.postgresql
        pkgs.python39Packages.psycopg2
	];

}