// Auto-generated code. Do not edit.
namespace myTiles {
    //% fixedInstance jres blockIdentity=images._tile
    export const tile1 = image.ofBuffer(hex``);
    //% fixedInstance jres blockIdentity=images._tile
    export const tile2 = image.ofBuffer(hex``);
    //% fixedInstance jres blockIdentity=images._tile
    export const tile3 = image.ofBuffer(hex``);
    //% fixedInstance jres blockIdentity=images._tile
    export const tile4 = image.ofBuffer(hex``);
    //% fixedInstance jres blockIdentity=images._tile
    export const tile5 = image.ofBuffer(hex``);
    //% fixedInstance jres blockIdentity=images._tile
    export const tile7 = image.ofBuffer(hex``);
    //% fixedInstance jres blockIdentity=images._tile
    export const tile6 = image.ofBuffer(hex``);

    helpers._registerFactory("tile", function(name: string) {
        switch(helpers.stringTrim(name)) {
            case "hitbox":
            case "tile1":return tile1;
            case "projectile":
            case "tile2":return tile2;
            case "marisaShot":
            case "tile3":return tile3;
            case "marisa":
            case "tile4":return tile4;
            case "redBall":
            case "tile5":return tile5;
            case "damageFlicker":
            case "tile7":return tile7;
            case "redBall0":
            case "tile6":return tile6;
        }
        return null;
    })

}
// Auto-generated code. Do not edit.
