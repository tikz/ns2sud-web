PLAYER_STATS = 'select ps.playerName, ps.hiveSkill, ps.marineHiveSkill, ps.alienHiveSkill, ps.steamId, ps.roundsPlayed, ps.timePlayed1/60/60 marineTime, ps.timePlayed2/60/60 alienTime, ps.commanderTime/60/60 commanderTime, ps.kills/ps.deaths kdr, ps.lastSeen, ps.discordTag, ps.discordAvatar from PlayerStats ps where ps.steamId = %s'

PLAYER_WEAPON_ACC = 'select weapon, avg((hits-onosHits)/(hits+misses-onosHits)) acc from PlayerWeaponStats where steamId = %s group by weapon'

PLAYER_WINS = 'select ri.roundId, ri.roundDate, prs.teamNumber, if(prs.teamNumber = ri.winningTeam, 1, 0) win from PlayerRoundStats prs inner join RoundInfo ri on ri.roundId = prs.roundId where prs.steamId = %s'

PLAYER_OTHER_NAMES = 'select playerName from PlayerRoundStats where steamId = %s group by playerName order by roundId desc limit 10'

PLAYER_ACTIVITY = 'select ri.roundDate, prs.timePlayed/60/60 hoursPlayed from PlayerRoundStats prs inner join RoundInfo ri on ri.roundId = prs.roundId where prs.steamId = %s'

PLAYER_CLASSTIME = 'select c.class, classTime/60/60 classTime from (select class from PlayerClassStats group by class) c left join (select class, sum(classTime) classTime from PlayerClassStats where steamId = %s group by class) pc on pc.class = c.class'


def limit(query):
    return query + ' limit %s, %s'


def count(query):
    return f'select count(*) total_count from ({query}) a'


MATCHES = 'select * from RoundInfo where roundId like %s or mapName like %s order by roundDate desc'

PLAYERS = 'select * from (select ps.steamId, ps.playerName, ps.hiveSkill, ps.timePlayed, ps.lastSeen, GROUP_CONCAT(DISTINCT prs.playerName SEPARATOR ", " ) as name_list, discordAvatar from PlayerStats ps LEFT JOIN PlayerRoundStats prs on prs.steamId = ps.steamId group by ps.steamId order by ps.lastSeen desc) players where name_list like %s'

UPDATE_DISCORD_DATA = 'update PlayerStats set discordId = %s, discordTag = %s, discordAvatar = %s where steamId = %s'

NEW_PLAYERS = 'select ri.roundDate, prs.steamId from PlayerRoundStats prs inner join RoundInfo ri on ri.roundId = prs.roundId group by steamId order by ri.roundDate'

MATCHES_WEEK = 'select roundId, roundDate from RoundInfo'
